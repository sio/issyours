
import os

from issyours_github.fetcher import *

token = os.environ.get('ISSYOURS_GITHUB_TOKEN')
gh = GitHubAPICaller(token)
resp = gh.get('https://api.github.com/repos/sio/scrapehelper')
#print(readable(resp))
