'''
Interact with GitHub REST API (v3)
https://developer.github.com/v3
'''


import json
import logging
import threading
import time
from datetime import datetime, timezone
from functools import total_ordering
from urllib.parse import urljoin

import requests

log = logging.getLogger('issyours.' + __name__.strip('issyours_'))



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
        '''Sleep until rate limit is reset'''
        with self.lock:
            if self.remaining is not None and not self.remaining:
                log.debug('Sleeping until rate limit is reset')
                time.sleep(max(self.reset_time - self.clock(), 0))


    def update(self, response):
        '''Update rate limit stats from HTTP response headers'''
        with self.lock:
            self.reset_time = int(response.headers['X-RateLimit-Reset'])
            self.remaining = int(response.headers['X-RateLimit-Remaining'])



class GitHubAPICaller:
    '''
    Low level read only GitHub REST API (v3) client
    '''

    API_ROOT = 'https://api.github.com'
    USER_AGENT = 'Issue backup fetcher v0.0.1 <https://github.com/sio/issyours/>'


    def __init__(self, token):
        '''Initialize API client with OAuth token'''
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
        '''Initialize API client with OAuth token'''
        self.api = GitHubAPICaller(token)


    def issues(self, owner, repo, since=None):
        '''Iterate over issue dictionaries'''
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
                    response = self.api.single(url=url, since=since)
                    data = response.json()
                    if 'Last-Modified' in response.headers:
                        data['header-last-modified'] = response.headers['Last-Modified']
                    yield data
                except GitHubNotModifiedException:
                    pass


    def comments(self, owner=None, repo=None, issue_no=None, since=None, url=None):
        '''Iterate over comment dictionaries'''
        kwargs = {}
        if not url:
            kwargs['endpoint'] = 'repos/{owner}/{repo}/issues/{number}/comments'.format(
                owner=owner,
                repo=repo,
                number=issue_no
            )
        else:
            kwargs['url'] = url
        kwargs['params'] = {'per_page': 100}
        if since:
            kwargs['params']['since'] = GitHubTimestamp(since).isotime

        for response in self.api.pages(**kwargs):
            for comment in response.json():
                yield comment


    def events(self, owner=None, repo=None, issue_no=None, since=None, url=None):
        '''Iterate over comment dictionaries'''
        kwargs = {}
        if not url:
            kwargs['endpoint'] = 'repos/{owner}/{repo}/issues/{number}/events'.format(
                owner=owner,
                repo=repo,
                number=issue_no
            )
        else:
            kwargs['url'] = url
        kwargs['params'] = {'per_page': 100}
        if since:
            kwargs['params']['since'] = GitHubTimestamp(since).isotime

        for response in self.api.pages(**kwargs):
            for event in response.json():
                yield event


    def person(self, nickname=None, since=None, url=None):
        '''Get information about specific GitHub user'''
        kwargs = {'since': since}
        if not url:
            kwargs['endpoint'] = 'users/{}'.format(nickname)
        else:
            kwargs['url'] = url
        return self.api.single(**kwargs).json()



@total_ordering
class GitHubTimestamp:
    '''
    Timestamps as accepted by GitHub API.
    All timezones must be converted to UTC before instanciating this object.
    '''

    HEADER_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
    ISO_FORMAT = '%Y-%m-%dT%H:%M:%SZ'


    def __init__(self, dtime=None, header=None, isotime=None, unix=None):
        '''
        Create timestamp object either from datetime object or from string
        in one of common formats
        '''
        if dtime:
            if isinstance(dtime, datetime):
                self.datetime = dtime
            elif isinstance(dtime, type(self)):
                self.datetime = dtime.datetime
            else:
                raise TypeError('expected datetime object, got {}'.format(dtime.__class__.__name__))
        elif header:
            self.datetime = datetime.strptime(header, self.HEADER_FORMAT)
        elif isotime:
            self.datetime = datetime.strptime(isotime, self.ISO_FORMAT)
        elif unix:
            self.datetime = datetime.utcfromtimestamp(int(unix))
        self.datetime = self.datetime.replace(tzinfo=timezone.utc)


    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.isotime)


    def __str__(self):
        return self.isotime


    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.datetime == other.datetime
        else:
            return NotImplemented


    def __lt__(self, other):
        if isinstance(other, type(self)):
            return self.datetime < other.datetime
        else:
            return NotImplemented


    @property
    def header(self):
        '''Timestamp used in API headers'''
        return datetime.strftime(self.datetime, self.HEADER_FORMAT)


    @property
    def isotime(self):
        '''ISO timestamp format'''
        return datetime.strftime(self.datetime, self.ISO_FORMAT)


    @property
    def unix(self):
        '''Unix epoch timestamp'''
        return int(self.datetime.timestamp())
