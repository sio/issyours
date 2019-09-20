'''
Common methods for reading issues data from any storage
'''


from abc import ABC, abstractmethod

from issyours.lazy import LazyAwareCache, LazyObject



class ReaderBase(ABC):
    '''
    Abstract base class that implements caching and lazy evaluation for any
    issue reader
    '''

    ISSUE_CACHE_SIZE = 50
    PERSON_CACHE_SIZE = 50


    @abstractmethod
    def __init__(self):
        self._issues_cache = LazyAwareCache(maxsize=self.ISSUE_CACHE_SIZE)
        self._persons_cache = LazyAwareCache(maxsize=self.PERSON_CACHE_SIZE)


    @abstractmethod
    def issue_uids(self, sort_by='created_at', desc=True):
        '''Yield unique identificators for all issues contained in Storage'''


    @abstractmethod
    def person_uids(self):
        '''Yield unique identificators for all persons contained in Storage'''


    @abstractmethod
    def _read_issue(self, uid):
        '''Return a single Issue object from Storage'''


    @abstractmethod
    def _read_person(self, login):
        '''Return a single Person object from storage'''


    @abstractmethod
    def _get_comments(self, issue, sort_by='created_at', desc=False):
        '''Yield comments for a given issue object'''


    @abstractmethod
    def _get_events(self, issue, sort_by='created_at', desc=False):
        '''Yield events for a given issue object'''


    def issues(self, sort_by='created_at', desc=True):
        '''Yield Issue objects in the specified order'''
        for uid in self.issue_uids(sort_by, desc):
            yield self.issue(uid)


    def issue(self, uid):
        '''
        Return a single Issue object from Storage.
        Use cached values and lazy evaluation whenever possible.
        '''
        return lazy_method(cache=self._issues_cache,
                           method=self._read_issue,
                           key=uid)


    def persons(self):
        '''
        Yield Person objects in arbitrary order
        '''
        for uid in self.person_uids():
            yield self.person(uid)


    def person(self, login):
        '''
        Return a single Person object from Storage.
        Use cached values and lazy evaluation whenever possible.
        '''
        return lazy_method(cache=self._persons_cache,
                           method=self._read_person,
                           key=login)


def lazy_method(cache, method, key):
    '''Implementation of lazy method'''
    try:
        return cache[key]
    except KeyError:
        value = LazyObject(method, key)
        cache[key] = value
        return value
