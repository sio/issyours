'''
Common methods for reading issues data from any storage
'''


from abc import ABC, abstractmethod
from types import SimpleNamespace
from weakref import WeakValueDictionary



ISSUE_CACHE_SIZE = 50



class ReaderBase(ABC):


    @abstractmethod
    def __init__(self):
        self._issues_cache = MultiCache(maxsize=ISSUE_CACHE_SIZE)


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



class LazyObject:
    '''Delay object initialization until any of its members are accessed'''


    def __init__(self, constructor, *a, **ka):
        self._lazy = LazyMetadata(constructor, a, ka)


    def __getattr__(self, attr):
        self._lazy.init()
        return getattr(self._lazy.inner, attr)


    def __setattr__(self, attr, value):
        if attr == '_lazy':
            return super().__setattr__(attr, value)
        self._lazy.init()
        return setattr(self._lazy.inner, attr, value)


    def __repr__(self):
        if self._lazy.inner is None:
            return '<{}: constructor={}>'.format(self.__class__.__name__, self._lazy.constructor)
        else:
            return '<{}: inner={}>'.format(self.__class__.__name__, self._lazy.inner)



class LazyMetadata(SimpleNamespace):
    '''Remember metadata required to create inner object'''


    def __init__(self, constructor, args, kwargs):
        super().__init__(constructor=constructor, args=args, kwargs=kwargs, inner=None)


    def init(self):
        '''Actually initialize inner object'''
        self.inner = self.constructor(*self.args, **self.kwargs)
        if self.inner is None:
            raise ValueError('constructor returned None: {}'.format(self.constructor))

        del self.constructor, self.args, self.kwargs
        self.init = lambda: None



class MultiCache:
    '''Multiparadigm cache with dict-like interface'''
    # TODO: MultiCache is not thread safe

    def __init__(self, maxsize=128):
        self._weak_cache = WeakValueDictionary()
        self._strong_cache = dict()
        self._maxsize = maxsize
        self._cache_worth = dict()
        self._lru_clock = 0


    def __repr__(self):
        return '<{cls}: weaksize={weaksize}, lrusize={lrusize}, maxsize={maxsize}>'.format(
            cls=self.__class__.__name__,
            weaksize=len(self._weak_cache),
            lrusize=len(self._strong_cache),
            maxsize=self._maxsize,
        )


    def __setitem__(self, key, value):
        self._weak_cache[key] = value
        self._strong_cache[key] = value

        self._lru_clock += 1
        self._cache_worth[key] = self._lru_clock

        self._drop()


    def __getitem__(self, key):
        value = self._weak_cache[key]
        self._lru_clock += 1
        self._cache_worth[key] = self._lru_clock
        return value


    def _drop(self):
        '''Drop items that are worth the lowest'''
        while len(self._strong_cache) > self._maxsize:
            garbage = sorted(self._cache_worth, key=self._cache_worth.get)[0]
            self._strong_cache.pop(garbage)
            self._cache_worth.pop(garbage)


    def __contains__(self, key):
        return key in self._weak_cache
