'''
Read GitHub issues from JSON files on local filesystem
'''


import json
import logging
import os
from urllib.parse import urlparse

from markdown import markdown
from markdown.extensions import fenced_code, codehilite, nl2br

from issyours.data import (
    Issue,
    IssueAttachment,
    IssueLabel,
    Person,
)
from issyours.reader import ReaderBase
from issyours_github.fetcher import attachment_urls
from issyours_github.storage import GitHubFileStorageBase
from issyours_github.api import GitHubTimestamp

log = logging.getLogger('issyours.' + __name__.strip('issyours_'))



class GitHubReader(ReaderBase):
    '''
    Read GitHub issues from local files fetched by GitHubFetcher
    '''

    def __init__(self, repo, directory):
        super().__init__()
        self.storage = GitHubFileStorageBase(repo, directory)


    def _read_issue(self, uid):
        log.debug('Reading issue #{} from local backup'.format(uid))
        filepath = self.storage.issue_path(issue_no=uid)
        with open(filepath, 'r') as f:
            data = json.load(f)
        issue = Issue(
            reader=self,
            uid=uid,
            author=Person(reader=self, nickname=''), # TODO: Person
            status=data['state'],
            title=data['title'],
            body=render_markdown(data['body']),
            url=data['html_url'],
            labels=[
                IssueLabel(name=l['name'], color='#' + l['color'])
                for l in data['labels']
            ],
            assignees=None, # TODO: Person
            created_at=GitHubTimestamp(isotime=data['created_at']).datetime,
            modified_at=GitHubTimestamp(isotime=data['updated_at']).datetime,
            fetched_at=self._fetched_at(uid),
            closed_at=GitHubTimestamp(isotime=data['closed_at']).datetime \
                      if data['closed_at'] else None,
            attachments=make_attachments(self.storage, data),
        )
        return issue


    def issue_uids(self, sort_by='created', desc=True):
        ids = next(os.walk(self.storage.issue_dir()))[1]
        if sort_by == 'created':
            return sorted(ids, key=int, reverse=desc)
        else:
            raise NotImplementedError('{} does not support sorting by {!r}'.format(
                self.__class__.__name__,
                sort_by
            ))


    def _fetched_at(self, issue_no):
        '''Read modification time from filesystem'''
        stamp = self.storage._stamp_path(issue_no)
        unix = os.path.getmtime(stamp)
        return GitHubTimestamp(unix=unix).datetime


def make_attachments(storage, issue_data, comment_data=None):
    '''
    Return a generator that yields attachment objects for a particular
    issue or a comment
    '''
    attachments = []

    if comment_data:
        body = comment_data['body']
    else:
        body = issue_data['body']
        patch_path = storage.patch_path(issue_data)
        if os.path.exists(patch_path):
            attachments.append((
                os.path.basename(patch_path),
                issue_data['pull_request']['html_url'],
                patch_path,
            ))

    linked_files = ((url, storage.attachment_path(issue_data, url))
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
            yield IssueAttachment(name=name, url=url, stream=open(filepath, 'rb'))

    return generator


def make_filename(url, filepath):
    '''Generate filename from the source url and the path of the file on disk'''
    # GitHub urls that we source attachments from are pretty clean already
    # so there is no need for MIME magic for now
    parsed = urlparse(url)
    return parsed.path.split('/')[-1]


MARKDOWN_CONFIG={
    'extensions': [x.makeExtension() for x in [
        fenced_code,
        codehilite,
        nl2br,
    ]],
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
