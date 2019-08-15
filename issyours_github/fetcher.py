'''
Create a backup of GitHub issues in JSON files on local filesystem
'''

import json
import logging
import os
from datetime import datetime
from tempfile import mkstemp

from issyours_github.api import GitHubAPI, GitHubTimestamp
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
        super().__init__(repo, directory)
        self.api = GitHubAPI(token)
        self._last_modified = None


    def fetch(self):
        owner, project = self.repo.split('/')

        since = self.read_stamp()
        log.info('Fetching issues for %r (modified since: %s)', self.repo, since)

        for issue in self.api.issues(owner, project, since):
            since = self.read_stamp(issue['number'])
            self.last_modified = GitHubTimestamp(isotime=issue['updated_at'])
            write_json(issue, self.issue_path(issue))
            log.info('Saved issue #%s', issue['number'])

            comments_url = issue['comments_url']
            for comment in self.api.comments(url=comments_url, since=since):
                write_json(comment, self.comment_path(issue, comment))
                log.info('Saved comment #%s', comment['id'])

            events_url = issue['events_url']
            for event in self.api.events(url=events_url, since=since):
                write_json(event, self.event_path(issue, event))
                log.info('Saved event #%s', event['id'])

            self.write_stamp(issue)
        self.write_stamp()


    @property
    def last_modified(self):
        '''
        The newest Last-Modified value seen by this instance
        (GitHubTimestamp object)
        '''
        if self._last_modified is None:
            timestamp = self.read_stamp()
            if timestamp is not None:
                self._last_modified = GitHubTimestamp(unix=timestamp)
            else:
                raise ValueError('Last-Modified has not been set yet')
        return self._last_modified


    @last_modified.setter
    def last_modified(self, value):
        if self._last_modified is None \
        or self._last_modified < value:
            self._last_modified = value


    def read_stamp(self, issue_no=None):
        '''Read timestamp files left from previous runs'''
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
