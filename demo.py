
import os
from datetime import datetime

from issyours_github.api import *
from issyours_github.fetcher import *

token = os.environ.get('ISSYOURS_GITHUB_TOKEN')
gh_low_level = GitHubAPICaller(token)
gh = GitHubAPI(token)


def print_pagination():
    gh = gh_low_level
    print('Pagination support:')
    pages = gh.pages('repos/sio/LibPQ/issues', params=dict(per_page=2))
    for p in pages:
        print(type(p), [i['number'] for i in p.json()])
    print()


def print_issues(repo='sio/LibPQ', since=None):
    owner, project = repo.split('/')
    for issue in gh.issues(owner, project, since=since):
        data = issue
        print(data['header-last-modified'], data['updated_at'], data['number'], data['title'])
    return data
