'''
Interact with GitHub REST API (v3)
https://developer.github.com/v3
'''


import json
import logging
import threading
import time
from urllib.parse import urljoin
from datetime import datetime

import requests



log = logging.getLogger('readissues.' + __name__.strip('readissues_'))



class GitHubRateLimitError(RuntimeError):
    '''Raised when GitHub rate limit has been exceeded'''



class GitHubAPIError(RuntimeError):
    '''Raised when some other unrecoverable API error occurs'''



class GitHubNotModifiedException(Exception):
    '''Raised when the API response was not modified since the last fetch'''



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
    Low level read only GitHub REST API (v3) client
    '''

    API_ROOT = 'https://api.github.com'
    USER_AGENT = 'Issue backup fetcher v0.0.1 <https://github.com/sio/readissues/>'


    def __init__(self, token):
        self._rate_limit = GitHubRateLimit()

        session = requests.Session()
        session.headers.update({
            'Accept': ('application/vnd.github.v3+json,'
                       'application/vnd.github.symmetra-preview+json,'
                       'application/vnd.github.squirrel-girl-preview+json'),
            'Authorization': 'token {}'.format(token),
            'User-Agent': self.USER_AGENT,
        })
        session.timeout = 5
        self._requests = session


    def single(self, endpoint=None, params=None, since=None, url=None):
        '''Fetch a single API response'''
        return next(self.pages(endpoint, params, since, url))


    def pages(self, endpoint=None, params=None, since=None, url=None):
        '''Iterate over paginated API responses'''
        headers = self._headers(since=since)
        response = self._call(endpoint, params, headers, url)
        yield response
        while 'next' in response.links:
            response = self._call(url=response.links['next']['url'], headers=headers)
            yield response


    def _get(self, url, *a, **ka):
        '''Execute GET request to a given URL'''
        self._rate_limit.sleep()
        response = self._requests.get(url, *a, **ka)
        self._rate_limit.update(response)
        self._check(response)
        return response


    def _call(self, endpoint=None, params=None, headers=None, url=None):
        '''Make a single API call'''
        if endpoint:
            url = urljoin(self.API_ROOT, endpoint)
        if not url:
            raise ValueError('either url or endpoint must be provided')
        return self._get(url, params=params, headers=headers)


    def _check(self, response):
        '''Check response for common error conditions'''
        if response.status_code == 200:
            return

        if response.status_code == 304:  # Not Modified
            raise GitHubNotModifiedException(response.url)

        if response.status_code == 403 \
        and response.headers['X-RateLimit-Remaining'] == '0':
            raise GitHubRateLimitError(readable(response))

        if response.status_code == 401:
            raise GitHubAPIError(response.json().get('message', 'Unknown API error'))

        response.raise_for_status()  # Any errors not handled above


    def _headers(self, since=None):
        '''Build extra headers for common use cases'''
        headers = {}
        if since:
            headers['If-Modified-Since'] = GitHubTimestamp(since).header
        return headers



class GitHubAPI:
    '''
    High level read only GitHub REST API (v3) client
    '''

    def __init__(self, token):
        self.api = GitHubAPICaller(token)


    def issues(self, owner, repo, since=None):
        endpoint = 'repos/{owner}/{repo}/issues'.format(owner=owner, repo=repo)
        params = {
            'filter': 'all',
            'state': 'all',
            'per_page': 100,
        }
        if since:
            params['since'] = GitHubTimestamp(since).isotime

        for response in self.api.pages(endpoint, params=params):
            for issue in response.json():
                url = issue['url']
                try:
                    yield self.api.single(url=url, since=since).json()
                except GitHubNotModifiedException:
                    pass


    def issue(self, owner, repo, issue_no, since=None):
        endpoint = 'repos/{owner}/{repo}/issues/{number}'.format(
            owner=owner,
            repo=repo,
            number=issue_no,
        )
        return self.api.single(endpoint, since=since).json()


    def comments(self, owner, repo, issue_no, since=None):
        pass



class GitHubTimestamp:
    '''
    Timestamps as accepted by GitHub API.
    All timezones must be converted to UTC before instanciating this object.
    '''

    HEADER_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
    ISO_FORMAT = '%Y-%m-%dT%H:%M:%SZ'


    def __init__(self, dtime=None, header=None, isotime=None):
        if dtime:
            if isinstance(dtime, datetime):
                self.datetime = dtime
                return
            else:
                raise TypeError('expected datetime object, got {}'.format(dtime.__class__.__name__))
        if header:
            self.datetime = datetime.strptime(header, self.HEADER_FORMAT)
            return
        if isotime:
            self.datetime = datetime.strptime(isotime, self.ISO_FORMAT)
            return


    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.isotime)


    @property
    def header(self):
        '''Timestamp used in API headers'''
        return datetime.strftime(self.datetime, self.HEADER_FORMAT)


    @property
    def isotime(self):
        '''ISO timestamp format'''
        return datetime.strftime(self.datetime, self.ISO_FORMAT)



def readable(response, payload=True):
    '''Make response readable'''
    overview = dict(
        status = response.status_code,
        headers = dict(response.headers),
        payload = response.json() if payload else '<...>',
    )
    return json.dumps(overview, indent=2, sort_keys=True)
