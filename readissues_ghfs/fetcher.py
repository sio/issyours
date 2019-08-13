'''
Create a backup of GitHub issues in JSON files on local filesystem
'''


import json
import logging

from scrapehelper.fetch import FetcherMeta



log = logging.getLogger('readissues.' + __name__.strip('readissues_'))



class GitHubRateLimitError(RuntimeError):
    '''Raised when GitHub rate limit has been exceeded'''



class GitHubAPICaller(metaclass=FetcherMeta):
    '''
    Simplistic GitHub REST API (v3) Client
    '''

    root = 'https://api.github.com'

    USER_AGENT = 'Issue backup fetcher v0.0.1 <https://github.com/sio/readissues/>'
    RATELIMIT_CALLS = 5000
    RATELIMIT_INTERVAL = 60*60  # 1 hour
    TIMEOUT = 5


    def __init__(self, token):
        self._requests.headers.update({
            'Accept': ('application/vnd.github.v3+json,'
                       'application/vnd.github.squirrel-girl-preview+json'),
            'Authorization': 'token {}'.format(token),
        })


    def get(self, url, *a, **ka):
        '''Execute GET request to a given URL'''
        with self.rate_limit:
            response = self._requests.get(url, *a, **ka)
        self._check(response)
        return response


    def _check(self, response):
        '''Check response for common error conditions'''
        api_remaining = response.headers.get('X-RateLimit-Remaining')
        if api_remaining:
            api_remaining = int(api_remaining)
            if self.rate_limit.remaining > api_remaining:
                log.debug(
                    'Adjusting %s rate limit from %s to %s',
                    self.__class__.__name__,
                    self.rate_limit.remaining,
                    api_remaining
                )
                self.rate_limit.remaining = api_remaining

        if response.status_code == 200:
            return

        if response.status_code == 403 \
        and response.headers['X-RateLimit-Remaining'] == '0':
            raise GitHubRateLimitError(readable(response))



def readable(response):
    '''Make response readable'''
    overview = dict(
        status = response.status_code,
        headers = dict(response.headers),
        payload = response.json(),
    )
    return json.dumps(overview, indent=2, sort_keys=True)
