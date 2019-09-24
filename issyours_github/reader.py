'''
Read GitHub issues from JSON files on local filesystem
'''


import json
import logging
import os
from glob import glob
from typing import Mapping
from urllib.parse import urlparse

from markdown import markdown
from markdown.extensions import fenced_code, codehilite, nl2br

from issyours.data import (
    Issue,
    IssueAttachment,
    IssueComment,
    IssueEvent,
    IssueLabel,
    Person,
)
from issyours.reader import ReaderBase
from issyours_github.fetcher import attachment_urls
from issyours_github.storage import GitHubFileStorage
from issyours_github.api import GitHubTimestamp

log = logging.getLogger('issyours.' + __name__.strip('issyours_'))



class GitHubReader(ReaderBase):
    '''
    Read GitHub issues from local files fetched by GitHubFetcher
    '''

    def __init__(self, repo, directory):
        if not os.path.isdir(directory):
            raise ValueError('not a directory: {}'.format(directory))
        super().__init__()
        self.storage = GitHubFileStorage(repo, directory)


    def __repr__(self):
        return '{cls}(repo={repo!r}, directory={dir!r})'.format(
            cls=self.__class__.__name__,
            repo=self.storage.repo,
            dir=self.storage.directory,
        )


    def _read_issue(self, uid):
        log.debug('Reading issue #{} from local backup'.format(uid))
        filepath = self.storage.issue_path(issue_no=uid)
        with open(filepath, 'r', encoding=self.storage.ENCODING) as f:
            data = json.load(f)
        issue = Issue(
            reader=self,
            uid=uid,
            author=self.person(data['user']['login']),
            author_role=data['author_association'],
            status=data['state'],  # TODO: convert to consistent subset of statuses
            title=data['title'],
            body=render_markdown(data['body']),
            original_url=data['html_url'],
            labels=[
                IssueLabel(name=l['name'], color='#' + l['color'])
                for l in data['labels']
            ],
            assignees=[self.person(u['login']) for u in data['assignees']],
            created_at=GitHubTimestamp(isotime=data['created_at']).datetime,
            modified_at=GitHubTimestamp(isotime=data['updated_at']).datetime,
            fetched_at=self._fetched_at(uid),
            closed_at=GitHubTimestamp(isotime=data['closed_at']).datetime \
                      if data['closed_at'] else None,
            attachments=make_attachments(self.storage, data),
        )
        return issue


    def issue_uids(self, sort_by='created_at', desc=True):
        ids = next(os.walk(self.storage.issue_dir()))[1]
        if sort_by == 'created_at':
            return sorted(ids, key=int, reverse=desc)
        else:
            raise NotImplementedError('{} does not support sorting by {!r}'.format(
                self.__class__.__name__,
                sort_by
            ))


    def person_uids(self):
        for filename in glob(os.path.join(self.storage.person_dir(), '*.json')):
            yield os.path.splitext(os.path.basename(filename))[0]


    def _fetched_at(self, issue_no):
        '''Read modification time from filesystem'''
        stamp = self.storage._stamp_path(issue_no)
        unix = os.path.getmtime(stamp)
        return GitHubTimestamp(unix=unix).datetime


    def _read_person(self, login):
        log.debug('Reading account information for @{}'.format(login))
        person_file = self.storage.person_path(login)
        with open(person_file, 'r', encoding=self.storage.ENCODING) as f:
            data = json.load(f)
        image_file = self.storage.person_image(login)
        if os.path.exists(image_file):
            picture = open(image_file, 'rb')
        else:
            picture = None
        return Person(
            reader=self,
            nickname=login,
            fullname=data['name'],
            original_url=data['html_url'],
            picture=picture,
        )


    def _get_comments(self, issue, sort_by='created_at', desc=False):
        if not sort_by == 'created_at':
            raise ValueError('unsupported sorting method: {}'.format(sort_by))
        directory = os.path.dirname(self.storage.issue_path(issue_no=issue.uid))
        pattern = 'comment-*.json'
        for filename in sorted(glob(os.path.join(directory, pattern)), reverse=desc):
            with open(filename, encoding=self.storage.ENCODING) as f:
                data = json.load(f)
            yield IssueComment(
                issue=issue,
                author=self.person(data['user']['login']),
                author_role=data['author_association'],  # TODO: convert to consistent subset
                body=render_markdown(data['body']),  # TODO: emoji reactions
                created_at=GitHubTimestamp(isotime=data['created_at']).datetime,
                modified_at=GitHubTimestamp(isotime=data['updated_at']).datetime,
                attachments=make_attachments(self.storage, issue_no=issue.uid, comment_data=data),
            )


    def _get_events(self, issue, sort_by='created_at', desc=False):
        if not sort_by == 'created_at':
            raise ValueError('unsupported sorting method: {}'.format(sort_by))
        directory = os.path.dirname(self.storage.issue_path(issue_no=issue.uid))
        pattern = 'event-*.json'
        for filename in sorted(glob(os.path.join(directory, pattern)), reverse=desc):
            with open(filename, encoding=self.storage.ENCODING) as f:
                data = json.load(f)
            event_type = data['event']
            if event_type not in IssueEvent._known_events:
                continue
            if event_type == 'assigned':
                author_data = data['assigner']
            else:
                author_data = data['actor']
            author_uid = author_data.get('login') if author_data else None
            yield IssueEvent(
                issue=issue,
                author=self.person(author_uid) if author_uid else None,
                type=event_type,
                data=self._extract_event_data(data),  # TODO: review usefullness of individual fields
                created_at=GitHubTimestamp(isotime=data['created_at']).datetime,
            )



    def _extract_event_data(self, data):
        '''Transform GitHub event data into issyours event data'''
        good_keys = {
            # key: further nested path
            'assignee': ('login',),
            'commit_id': (),
            'dismissed_review': ('dismissal_message',),
            'lock_reason': (),
            'milestone': (),
            'rename': (),
            'requester': (),
            'commit_id': (),
        }
        result = dict()
        for key, value in data.items():
            if not value:
                continue
            if key in good_keys:
                result[key] = _nested_dict_lookup(value, *good_keys[key])
            elif key in {'assignees', 'requested_reviewers'}:
                result[key] = [u['login'] for u in value]
            elif key in {'label', 'labels'}:
                if not 'labels' in result:
                    labels = result['labels'] = []
                if isinstance(value, Mapping):
                    value = [value,]
                for l in value:
                    labels.append(IssueLabel(l['name'], '#' + l['color']))
        if 'assignee' in result:
            result['assignees'] = set(result.get('assignees', []) + [result['assignee']])
            result.pop('assignee')
        if 'assignees' in result:
            logins = result['assignees']
            result['assignees'] = [self.person(x) for x in logins]
        return result


def _nested_dict_lookup(dictionary, *keys, default=None):
    result = dictionary
    for key in keys:
        try:
            result = result[key]
        except KeyError:
            return default
    return result


def make_attachments(storage, issue_data=None, issue_no=None, comment_data=None):
    '''
    Return a generator that yields attachment objects for a particular
    issue or a comment
    '''
    attachments = []

    if comment_data:
        body = comment_data['body']
    else:
        body = issue_data['body']
        issue_no = issue_data['number']
        patch_path = storage.patch_path(issue_data)
        if os.path.exists(patch_path):
            attachments.append((
                os.path.basename(patch_path),
                issue_data['pull_request']['html_url'],
                patch_path,
            ))

    linked_files = ((url, storage.attachment_path(url, issue_no=issue_no))
                    for url in attachment_urls(body))
    for url, filepath in linked_files:
        if os.path.exists(filepath):
            attachments.append((
                make_filename(url, filepath),
                url,
                filepath,
            ))

    def generator():
        for name, url, filepath in attachments:
            yield IssueAttachment(name=name, original_url=url, stream=open(filepath, 'rb'))

    return generator


def make_filename(url, filepath):
    '''Generate filename from the source url and the path of the file on disk'''
    # GitHub urls that we source attachments from are pretty clean already
    # so there is no need for MIME magic for now
    parsed = urlparse(url)
    return parsed.path.split('/')[-1]


MARKDOWN_CONFIG={
    'extensions': [
        'markdown.extensions.fenced_code',
        'markdown.extensions.codehilite',
        'markdown.extensions.nl2br',
    ],
    'extension_configs': {
        'markdown.extensions.codehilite': {
            'css_class': 'highlight',
            'guess_lang': False,
        },
        'markdown.extensions.extra': {},
        'markdown.extensions.meta': {},
    },
    'output_format': 'html5',
}
def render_markdown(text):
    '''Render markdown as HTML following GitHub conventions'''
    return markdown(text, **MARKDOWN_CONFIG)
