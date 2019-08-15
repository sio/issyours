'''
Create a backup of GitHub issues in JSON files on local filesystem
'''

import json
import logging
import os
import re
from datetime import datetime
from tempfile import mkstemp

import requests

from issyours_github.api import GitHubAPI, GitHubTimestamp, GitHubNotModifiedException
from issyours_github.storage import GitHubFileStorageBase

log = logging.getLogger('issyours.' + __name__.strip('issyours_'))



class GitHubFetcher(GitHubFileStorageBase):
    '''
    Fetch GitHub issues data and store it on local filesystem
    '''

    ABOUT = 'GitHub Issues Archive made with <https://github.com/sio/issyours>'
    STAMP_FILE = 'fetcher.json'
    STAMP_VERSION = 1


    def __init__(self, repo, directory, token):
        '''Initialize fetcher with GitHub repo name, target directory and OAuth token'''
        super().__init__(repo, directory)
        self.api = GitHubAPI(token)
        self._last_modified = None
        self._persons_seen = set()


    def fetch(self):
        '''Fetch all issues modified since the last run'''
        owner, project = self.repo.split('/')

        since = self.read_stamp()
        log.info('Fetching issues for %r (modified since: %s)', self.repo, since)

        for issue in self.api.issues(owner, project, since):
            users = set()
            since = self.read_stamp(issue['number'])
            self.last_modified = GitHubTimestamp(isotime=issue['updated_at'])
            write_json(issue, self.issue_path(issue))
            log.info('Saved issue #%s', issue['number'])
            self.fetch_attachments(issue, issue['body'])

            if 'pull_request' in issue:
                patch_url = issue['pull_request']['patch_url']
                download(patch_url, self.patch_path(issue))
                log.info('Saved patch file for pull request #%s', issue['number'])

            comments_url = issue['comments_url']
            for comment in self.api.comments(url=comments_url, since=since):
                write_json(comment, self.comment_path(issue, comment))
                log.info('Saved comment #%s', comment['id'])
                users.add(comment['user']['login'])
                self.fetch_attachments(issue, comment['body'])

            events_url = issue['events_url']
            for event in self.api.events(url=events_url, since=since):
                write_json(event, self.event_path(issue, event))
                log.info('Saved event #%s', event['id'])
                if event.get('actor'):
                    users.add(event.get('actor').get('login'))

            users.add(issue['user']['login'])
            for assignee in issue['assignees']:
                users.add(assignee['login'])
            if issue['closed_by']:
                users.add(issue['closed_by']['login'])
            self.fetch_persons(nicknames=users, since=since)

            self.write_stamp(issue)
        self.write_stamp()


    def fetch_persons(self, nicknames, since=None):
        '''Fetch data about GitHub user. Execute only once for each nickname seen'''
        for nickname in nicknames:
            if not nickname or nickname in self._persons_seen:
                continue
            self._persons_seen.add(nickname)
            try:
                person = self.api.person(nickname, since)
                person_file = self.person_path(person=person)
                write_json(person, person_file)
                log.info('Saved user @%s', person['login'])
            except GitHubNotModifiedException:
                continue
            try:
                image_file = os.path.splitext(person_file)[0] + '.jpg'
                download(person['avatar_url'], image_file)
                log.info('Saved avatar for @%s', person['login'])
            except requests.HTTPError:
                log.debug('Can not fetch: %s', person['avatar_url'])


    def fetch_attachments(self, issue, body):
        '''Fetch attachments linked in the issue/comment body'''
        for url in attachment_urls(body):
            dest = self.attachment_path(issue, url)
            if os.path.exists(dest):
                continue
            try:
                download(url, dest)
                log.info('Saved attachment: %s', url)
            except requests.HTTPError:
                log.debug('Can not fetch: %s', url)


    @property
    def last_modified(self):
        '''
        The newest Last-Modified value seen by this instance
        (GitHubTimestamp object)
        '''
        if self._last_modified is None:
            timestamp = self.read_stamp()
            if timestamp is not None:
                self._last_modified = GitHubTimestamp(timestamp)
            else:
                raise ValueError('Last-Modified has not been set yet')
        return self._last_modified


    @last_modified.setter
    def last_modified(self, value):
        if self._last_modified is None \
        or self._last_modified < value:
            self._last_modified = value


    def read_stamp(self, issue_no=None):
        '''
        Read timestamp files left from previous runs.
        Return datetime object
        '''
        stamp_path = self._stamp_path(issue_no)
        if not os.path.exists(stamp_path):
            return None
        with open(stamp_path) as f:
            stamp = json.load(f)
        self._stamp_validate(stamp, issue_no)
        return datetime.utcfromtimestamp(stamp['timestamp'])


    def write_stamp(self, issue=None):
        '''Write signature file after successful completion of whole job or its atomic part'''
        if issue:
            issue_no = issue['number']
            timestamp = GitHubTimestamp(header=issue['header-last-modified']).unix
        else:
            issue_no = None
            timestamp = self.last_modified.unix
        stamp = dict(
            timestamp=timestamp,
            repo=self.repo,
            fetcher=self.__class__.__name__,
            about=self.ABOUT,
            stamp_version=self.STAMP_VERSION,
        )
        if issue_no:
            stamp['issue_no'] = issue_no
        dest = self._stamp_path(issue_no)
        write_json(stamp, dest)
        log.info('Saved timestamp file: %s', dest)


    def _stamp_path(self, issue_no=None):
        '''Calculate path to stamp file'''
        if issue_no:
            directory = self.issue_dir(issue_no=issue_no)
        else:
            directory = self.directory
        return os.path.join(directory, self.STAMP_FILE)


    def _stamp_validate(self, stamp, issue_no=None):
        '''Validate stamp file to avoid data corruption with overwriting'''
        validate = {
            'repo': self.repo,
            'fetcher': self.__class__.__name__,
            'stamp_version': self.STAMP_VERSION,
        }
        if issue_no:
            validate['issue_no'] = issue_no
        for title, correct in validate.items():
            received = stamp[title]
            if correct != received:
                raise FetcherStampValidationError(title, correct, received)
        if 'timestamp' not in stamp:
            raise FetcherStampValidationError('timestamp', 'any value', 'nothing')



class FetcherStampValidationError(ValueError):
    '''
    Raised when stamp data does not match current fetcher object.
    This will help to avoid data corruption with accidental overwriting.
    '''

    template = ('data on disk does not come from this fetcher: '
                '{title!r} was expected to be {correct!r} '
                'but got {received!r} instead')

    def __init__(self, title, correct, received):
        message = self.template.format(**locals())
        super().__init__(message)



def write_json(dictionary, filepath):
    '''Serialize a dictionary into a JSON file'''
    serialized = json.dumps(dictionary, indent=2, sort_keys=True, ensure_ascii=False)
    safe_write(filepath, serialized)


def safe_write(filepath, content, mode='w'):
    '''Safely (over)write a small file'''
    directory, filename = os.path.split(os.path.abspath(filepath))
    if not os.path.exists(directory):
        os.makedirs(directory)

    text_mode = 'b' not in mode
    if text_mode:
        content = content.encode('utf-8')

    tmp, tmppath = mkstemp(prefix=filename, dir=directory, text=text_mode)
    os.write(tmp, content)
    os.close(tmp)
    os.replace(tmppath, filepath)


def attachment_urls(body, _pattern=re.compile(
            '('
            r'http[s]?://[^/]*githubusercontent.com/[\.\w/&%+-]+'
            r'|http[s]?://github.com/\w+/\w+/files/[\.\w/&%+-]+'
            ')')):
    '''Detect attachment URLs in the body of GitHub issue/comment'''
    # URL regex from http://urlregex.com/
    # http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+
    if body:
        yield from _pattern.findall(body)
    else:
        yield from ()


def download(url, dest):
    '''Download regular files from web'''
    response = requests.get(url, allow_redirects=True)
    response.raise_for_status()
    with open(dest, 'wb') as output:
        output.write(response.content)
