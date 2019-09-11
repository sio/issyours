'''
Read GitHub issues from JSON files on local filesystem
'''


import json
import logging
import os

from issyours.data import (
    Issue,
    IssueLabel,
    Person,
)
from issyours.reader import ReaderBase
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
            author=Person(reader=self), # TODO: Person
            status=data['state'],
            title=data['title'],
            body=data['body'], # TODO: html
            url=data['html_url'],
            labels=[
                IssueLabel(name=l['name'], color='#' + l['color'])
                for l in data['labels']
            ],
            assignees=None, # TODO: Person
            created_at=GitHubTimestamp(isotime=data['created_at']).datetime,
            modified_at=GitHubTimestamp(isotime=data['updated_at']).datetime,
            fetched_at=None, # TODO: timestamp from fs
            closed_at=GitHubTimestamp(isotime=data['closed_at']).datetime \
                      if data['closed_at'] else None,
            #attachments=None, # TODO
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
