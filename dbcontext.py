from google.cloud import ndb
from google.cloud.ndb import context as context_module
from functools import wraps
from memcache import global_cache


# The NDB client must be created in order to use NDB, and any use of NDB must be within the context of a call to dbcontext
datastore_client = ndb.Client()

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

