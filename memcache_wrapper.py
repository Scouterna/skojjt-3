# from google.cloud.ndb.global_cache import MemcacheCache, RedisCache
from google.appengine.api import memcache as my_memcache
import pickle

global_cache = my_memcache

class MemcacheWrapper():
    def get(self, key:str) -> object | None:
        """Get entities from the cache.

        Arguments:
            key: Mapping of keys to serialized entities.
        Returns:
            the value associated with the key or None if no value was found            
        """        
        return my_memcache.get(key)

    def get_unpickled(self, key:str):
        """Get objects that needs to be unpickled from the cache.

        Arguments:
            key: Mapping of keys to serialized entities.
        Returns:
            the value associated with the key or None if no value was found            
        """
        result = my_memcache.get(key)
        if not result:
            return None
        return pickle.loads(result)

    def set(self, key:str, value, expires=None) -> None:
        """Store entities in the cache.

        Arguments:
            key: Mapping of keys to serialized entities.
            value: the value to store for this key
            expires: Number of seconds until value expires.
        """        
        my_memcache.set(key, value)

    def set_pickled(self, key:str, value, expires=None) -> None:
        """Store objects that needs to be pickled in the cache.

        Arguments:
            key: Mapping of keys to serialized entities.
            value: the object that need to be pickled
            expores: time in seconds until the value expires
        """
        pickled = pickle.dumps(value)
        self.set(key, pickled)

    def replace(self, key:str, value, expires=None):
        """Replace values in the cache

        Arguments:
            key: Mapping of keys to serialized entities.
            value: the object that need to be pickled
            expores: time in seconds until the value expires
        """                
        my_memcache.set(key, value)

    def remove(self, key:str):
        my_memcache.delete(key)

    def replace_pickled(self, key:str, value, expires=None):
        self.remove(key)
        self.set_pickled(key, value)

#memcache = MemcacheWrapper()


# global_cache = RedisCache.from_environment()
# class MemcachRediseWrapper():
#     def get(self, key:str) -> object | None:
#         """Get entities from the cache.

#         Arguments:
#             key: Mapping of keys to serialized entities.
#         Returns:
#             the value associated with the key or None if no value was found            
#         """        
#         result = global_cache.get(key) # type: list[str]
#         if isinstance(result, list) and len(result) > 0 and result[0]:
#             return result[0].decode()
#         return None

#     def get_unpickled(self, key:str) -> object:
#         """Get objects that needs to be unpickled from the cache.

#         Arguments:
#             key: Mapping of keys to serialized entities.
#         Returns:
#             the value associated with the key or None if no value was found            
#         """        
#         result = global_cache.get(key) # type: list[str]
#         if isinstance(result, list) and len(result) > 0 and result[0]:
#             return pickle.loads(result[0])
#         return None

#     def set(self, key, value, expires=None) -> None:
#         """Store entities in the cache.

#         Arguments:
#             key: Mapping of keys to serialized entities.
#             value: the value to store for this key
#             expires: Number of seconds until value expires.
#         """        
#         items = dict()
#         items[key] = value
#         global_cache.set(items, expires)

#     def set_pickled(self, key, value, expires=None) -> None:
#         """Store objects that needs to be pickled in the cache.

#         Arguments:
#             key: Mapping of keys to serialized entities.
#             value: the object that need to be pickled
#             expores: time in seconds until the value expires
#         """                
#         items = dict()
#         items[key] = pickle.dumps(value)
#         global_cache.set(items, expires)

#     def replace(self, key, value, expires=None):
#         """Replace values in the cache

#         Arguments:
#             key: Mapping of keys to serialized entities.
#             value: the object that need to be pickled
#             expores: time in seconds until the value expires
#         """                
#         global_cache.delete([key])
#         self.set(key, value, expires)

#     def remove(self, key:str):
#         global_cache.delete([key])

#     def replace_pickled(self, key:str, value, expires=None):
#         global_cache.delete([key])
#         self.set_pickled(key, value, expires)


# memcache = MemcachRediseWrapper()
