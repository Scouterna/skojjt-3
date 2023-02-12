from google.cloud.ndb.global_cache import RedisCache
import pickle

# Assume REDIS_CACHE_URL is set in environment (or not).
# If left unset, this will return `None`, which effectively allows you to turn
# global cache on or off using the environment.
global_cache = RedisCache.from_environment()
# NOTE:  get will call redis.mget and always return a list
class MemcacheRedisWrapper():
    def get(self, key):
        result = global_cache.get(key) # type: list[str]
        if isinstance(result, list) and len(result) > 0:
            return result[0]
        return None

    def get_unpickled(self, key):
        result = global_cache.get(key) # type: list[str]
        if isinstance(result, list) and len(result) > 0:
            return pickle.loads(result[0])
        return None

    def set(self, key, value):
        items = dict()
        items[key] = value
        global_cache.set(items)

    def set_picked(self, key, value):
        items = dict()
        items[key] = pickle.dumps(value)
        global_cache.set(items)

    def replace(self, key, value):
        global_cache.delete([key])
        self.set(key, value)

    def replace_picked(self, key, value):
        global_cache.delete([key])
        self.set_picked(key, value)

memcache = MemcacheRedisWrapper()
