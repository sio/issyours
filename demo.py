
import os

from readissues_ghfs.fetcher import *

token = os.environ.get('READISSUES_GITHUB_TOKEN')
gh = GitHubAPICaller(token)
resp = gh.get('https://api.github.com/repos/sio/scrapehelper')
#print(readable(resp))
