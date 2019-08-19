'''
Lazy evaluation and caching tools
'''


from types import SimpleNamespace
from weakref import WeakValueDictionary



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
    '''
    Multistorage cache with dict-like interface

    This cache stores most recently used items in a regular Python dictionary
    and also keeps weak references to all seen items until they are garbage
    collected
    '''
    # TODO: MultiCache is not thread safe


    def __init__(self, maxsize=128):
        self._weak_cache = WeakValueDictionary()
        self._strong_cache = dict()
        self._maxsize = maxsize
        self._cache_worth = dict()
        self._lru_clock = 0


    def _droppable(self):
        '''
        Provide the sequence of cache keys that can be dropped safely.
        Return None if any cache item may be dropped without extra selection step
        '''
        # Intended to be implemented in child classes


    def _drop(self):
        '''Drop items that are worth the lowest to maintain max cache size'''
        oversize = len(self._strong_cache) - self._maxsize
        if oversize <= 0:
            return

        droppable_keys = self._droppable()
        if droppable_keys is not None:
            droppable_keys = set(droppable_keys)
            if oversize > len(droppable_keys):
                # In our use case this should never happen because _drop() is
                # being called after each __setitem__, so oversize can't be
                # more than 1
                raise ValueError('provided set of droppable keys is too small')

        for key in sorted(self._cache_worth, key=self._cache_worth.get):
            if len(self._strong_cache) > self._maxsize:
                if droppable_keys and key not in droppable_keys:
                    continue
                elif droppable_keys:
                    droppable_keys.remove(key)
                self._strong_cache.pop(key)
                self._cache_worth.pop(key)
            else:
                break


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


    def __contains__(self, key):
        return key in self._weak_cache


    def __repr__(self):
        return '<{cls}: weaksize={weaksize}, lrusize={lrusize}, maxsize={maxsize}>'.format(
            cls=self.__class__.__name__,
            weaksize=len(self._weak_cache),
            lrusize=len(self._strong_cache),
            maxsize=self._maxsize,
        )



class LazyAwareCache(MultiCache):
    '''Cache object that drops uninitialized LazyObjects first'''

    def _droppable(self):
        droppable_keys = set()
        for key, item in self._strong_cache.items():
            if item._lazy.inner is None:
                droppable_keys.add(key)
        if droppable_keys:
            return droppable_keys  # Select items to drop from this set
        else:
            return None  # Use all existing cache items
                         # if there are no uninitialized ones
