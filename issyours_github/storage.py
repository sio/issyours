'''
Common storage interaction methods used both by fetcher and reader
'''

import base64
import hashlib
import os

from issyours_github.api import GitHubTimestamp



class GitHubFileStorageBase:
    '''Common base class for fetcher and reader'''


    def __init__(self, repo, directory):
        self.repo = repo
        self.directory = directory


    def issue_dir(self, issue=None, issue_no=None):
        '''
        Path to the directory containing all data on a single issue.
        If no issue is specified, return top-level directory with all issues.
        '''
        elements = [self.directory, 'issues']
        if not issue_no and issue:
            issue_no = issue['number']
        if issue_no:
            elements.append(str(issue_no))
        return os.path.join(*elements)


    def issue_path(self, issue=None, issue_no=None):
        '''Path to the main issue JSON file'''
        return os.path.join(self.issue_dir(issue, issue_no), 'issue.json')


    def comment_path(self, issue, comment):
        '''Path to individual comment's JSON file'''
        filename = 'comment-{}-{}.json'.format(
            GitHubTimestamp(isotime=comment['created_at']).unix,
            comment['id']
        )
        return os.path.join(self.issue_dir(issue), filename)


    def event_path(self, issue, event):
        '''Path to individual event's JSON file'''
        filename = 'event-{}-{}.json'.format(
            GitHubTimestamp(isotime=event['created_at']).unix,
            event['id']
        )
        return os.path.join(self.issue_dir(issue), filename)


    def person_path(self, nickname=None, person=None):
        '''Path to individual person's JSON file'''
        if not nickname:
            nickname = person['login']
        return os.path.join(self.directory, 'people', '{}.json'.format(nickname))


    def attachment_path(self, issue, attach_url):
        '''Path to an attachment file'''
        directory = self.issue_dir(issue)

        hashed_name = hashlib.md5(attach_url.encode('utf-8')).digest()
        shorter_hash = base64.urlsafe_b64encode(hashed_name).decode('utf-8').rstrip('=')
        filename = 'attach-{}'.format(shorter_hash)

        return os.path.join(directory, filename)


    def patch_path(self, issue):
        '''Path to patch file'''
        return os.path.join(self.issue_dir(issue), 'attached.patch')


    def _stamp_path(self, issue_no=None):
        '''Calculate path to stamp file'''
        if issue_no:
            directory = self.issue_dir(issue_no=issue_no)
        else:
            directory = self.directory
        return os.path.join(directory, 'fetcher.json')
