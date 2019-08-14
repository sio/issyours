'''
Create a backup of GitHub issues in JSON files on local filesystem
'''


import json
import logging
import threading
import time
from urllib.parse import urljoin

import requests



log = logging.getLogger('readissues.' + __name__.strip('readissues_'))



class GitHubRateLimitError(RuntimeError):
    '''Raised when GitHub rate limit has been exceeded'''



class GitHubAPIError(RuntimeError):
    '''Raise when some other unrecoverable API error occurs'''



class GitHubRateLimit:
    '''Simple rate limiter for GitHub'''

    def __init__(self):
        self.lock = threading.RLock()
        self.clock = time.time
        self.reset_time = None
        self.remaining = None


    def __repr__(self):
        return '<{}: remaining={}, reset_time={}>'.format(
            self.__class__.__name__,
            self.remaining,
            self.reset_time,
        )


    def sleep(self):
        with self.lock:
            if self.remaining is not None and not self.remaining:
                log.debug('Sleeping until rate limit is reset')
                time.sleep(max(self.reset_time - self.clock(), 0))


    def update(self, response):
        with self.lock:
            self.reset_time = int(response.headers['X-RateLimit-Reset'])
            self.remaining = int(response.headers['X-RateLimit-Remaining'])



class GitHubAPICaller:
    '''
    Simplistic GitHub REST API (v3) Client
    '''

    API_ROOT = 'https://api.github.com'
    USER_AGENT = 'Issue backup fetcher v0.0.1 <https://github.com/sio/readissues/>'


    def __init__(self, token):
        self._rate_limit = GitHubRateLimit()

        session = requests.Session()
        session.headers.update({
            'Accept': ('application/vnd.github.v3+json,'
                       'application/vnd.github.squirrel-girl-preview+json'),
            'Authorization': 'token {}'.format(token),
            'User-Agent': self.USER_AGENT,
        })
        session.timeout = 5
        self._requests = session


    def single(self, endpoint, params=None):
        '''Fetch a single API response'''
        return self._call(endpoint, params).json()


    def pages(self, endpoint, params=None):
        '''Iterate over paginated API responses'''
        response = self._call(endpoint, params)
        yield response.json()
        while 'next' in response.links:
            response = self._get(response.links['next']['url'])
            yield response.json()


    def _get(self, url, *a, **ka):
        '''Execute GET request to a given URL'''
        self._rate_limit.sleep()
        response = self._requests.get(url, *a, **ka)
        self._rate_limit.update(response)
        self._check(response)
        return response


    def _call(self, endpoint, params=None):
        '''Make a single API call'''
        return self._get(urljoin(self.API_ROOT, endpoint), params=params)


    def _check(self, response):
        '''Check response for common error conditions'''
        if response.status_code == 200:
            return

        if response.status_code == 403 \
        and response.headers['X-RateLimit-Remaining'] == '0':
            raise GitHubRateLimitError(readable(response))

        if response.status_code == 401:
            raise GitHubAPIError(response.json().get('message', 'Unknown API error'))



def readable(response, payload=True):
    '''Make response readable'''
    overview = dict(
        status = response.status_code,
        headers = dict(response.headers),
        payload = response.json() if payload else '<...>',
    )
    return json.dumps(overview, indent=2, sort_keys=True)
