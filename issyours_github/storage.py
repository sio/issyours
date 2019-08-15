'''
Common storage interaction methods used both by fetcher and reader
'''

import os

from issyours_github.api import GitHubTimestamp



class GitHubFileStorageBase:
    '''Common base class for fetcher and reader'''


    def __init__(self, repo, directory):
        self.repo = repo
        self.directory = directory


    def issue_dir(self, issue=None, issue_no=None):
        '''Path to the directory containing all data on a single issue'''
        if not issue_no:
            issue_no = issue['number']
        return os.path.join(self.directory, str(issue_no))


    def issue_path(self, issue):
        '''Path to the main issue JSON file'''
        return os.path.join(self.issue_dir(issue), 'issue.json')


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
