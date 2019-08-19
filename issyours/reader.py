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


    @abstractmethod
    def __init__(self):
        self._issues_cache = LazyAwareCache(maxsize=self.ISSUE_CACHE_SIZE)


    @abstractmethod
    def issue_uids(self, sort_by='created', desc=True):
        '''Yield unique identificators for all issues contained in Storage'''


    @abstractmethod
    def _read_issue(self, uid):
        '''Return a single Issue object from Storage'''


    def issues(self, sort_by='created', desc=True):
        '''Yield Issue objects in the specified order'''
        for uid in self.issue_uids(sort_by, desc):
            yield self.issue(uid)


    def issue(self, uid):
        '''
        Return a single Issue object from Storage.
        Use cached values and lazy evaluation whenever possible.
        '''
        try:
            return self._issues_cache[uid]
        except KeyError:
            value = LazyObject(self._read_issue, uid)
            self._issues_cache[uid] = value
            return value
