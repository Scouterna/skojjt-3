# -*- coding: utf-8 -*-
from google.cloud import ndb
from google.cloud.ndb import context as context_module
from google.cloud.ndb.global_cache import RedisCache
import datetime
import logging
from functools import wraps

datastore_client = ndb.Client()

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

    def set(self, key, value):
        items = dict()
        items[key] = value
        global_cache.set(items)

    def replace(self, key, value):
        global_cache.delete([key])
        self.set(key, value)

memcache = MemcacheRedisWrapper()

# Assume GOOGLE_APPLICATION_CREDENTIALS is set in environment.
client = ndb.Client()
# decorator that adds a database context.
def dbcontext(func):
    @wraps(func) # needed to get unique function signature for flask url-mapping
    def wrapper(*args, **kwargs):
        current_context = context_module.get_context(False)
        if current_context is not None:
            return func(*args, **kwargs)
        else:
            with client.context(global_cache=global_cache): # create context with cache
                return func(*args, **kwargs)
    return wrapper


class PropertyWriteTracker(ndb.Model):
    _dirty = False

    def __init__(self, *args, **kw):
        self._dirty = False
        super(PropertyWriteTracker, self).__init__(*args, **kw)

    def __setattr__(self, key, value):
        if key[:1] != '_': # avoid all system properties and "_dirty"
            if self.__getattribute__(key) != value:
                self._make_dirty()
        super(PropertyWriteTracker, self).__setattr__(key, value)

    def _make_dirty(self):
        self._dirty = True

    def _not_dirty(self):
        self._dirty = False


class Semester(ndb.Model):
    year = ndb.IntegerProperty(required=True)
    ht = ndb.BooleanProperty(required=True)

    @staticmethod
    def getid(year, ht):
        return str(year) + ("ht" if ht else "vt")

    @staticmethod
    def create(year, ht):
        if year < 2016:
            raise ValueError("Invalid year %d" % year)
        return Semester(id=Semester.getid(year, ht), year=year, ht=ht)

    @staticmethod
    def getbyId(id_string):
        return Semester.get_by_id(id_string.replace('-',''))

    @staticmethod
    def getOrCreateCurrent():
        thisdate = datetime.datetime.now()
        ht = True if thisdate.month>6 else False
        year = thisdate.year
        semester = Semester.get_by_id(Semester.getid(year, ht))
        if semester == None:
            semester = Semester.create(year, ht)
            semester.put()
        return semester

    @staticmethod
    def getAllSemestersSorted(ascending=False):
        semesters=[]
        semesters.extend(Semester.query().order(-Semester.year, -Semester.ht).fetch())
        if len(semesters) == 0:
            semesters = [Semester.getOrCreateCurrent()]
        if ascending:
            semesters.reverse()
        return semesters

    def getname(self):
        return "%04d-%s" % (self.year, "ht" if self.ht else "vt")

    def getsortname(self):
        return "%04d.%d" % (self.year, 1 if self.ht else 0)

    def getMinDateStr(self):
        if self.ht:
            return "%04d-07-01" % (self.year)
        else:
            return "%04d-01-01" % (self.year)

    def getMaxDateStr(self):
        if self.ht:
            return "%04d-12-31" % (self.year)
        else:
            return "%04d-06-30" % (self.year)

