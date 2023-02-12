import logging
from xmlrpc.client import Boolean
from flask import request, render_template, redirect
from functools import wraps
from google.auth.transport import requests
import google.oauth2.id_token
from scoutnetuser import ScoutnetUser
import json
from memcache import memcache
import hashlib


def login():
    id_token = request.cookies.get("token")
    error_message = None
    times = None

    if id_token:
        user = get_user(id_token)

    return render_template(
        'login.html',
        user=user, error_message=error_message, times=times)


def checkAccess(func):
    '''
    Decorator for access check.
    Parameters:
        func: is the function to be decorator it needs to take a ScoutnetUser as first argument, func(user, *args, **kwargs)
    '''

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Verify Firebase auth.
        logging.info(f"{request.method} {request.url} {func.__name__} checkAccess wrapper")
        id_token = request.cookies.get("token")
        error_message = None
        claims = None
        if id_token:
            logging.info(f"{request.method} {request.url} {func.__name__} if id_token")
            user = get_user(id_token)
            try:
                # Verify the token against the Firebase Auth API. 
                # This verifies the token on each page load. 
                # For improved performance, we should cache results in an encrypted in session store 
                # see for instance: http://flask.pocoo.org/docs/1.0/quickstart/#sessions.
                if not user:
                    logging.info(f"{request.method} {request.url} {func.__name__} id_token not in cache")
                    firebase_request_adapter = requests.Request()
                    claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
                    user_data = claims['firebase']['sign_in_attributes']
                    user = parse_and_add_user(id_token, user_data)
                else:
                    logging.info(f"{request.method} {request.url} {func.__name__} id_token was in cache!")
                    user = user_cache[id_token]
                
                logging.info(f"{request.method} {request.url} {func.__name__} {user.getname()}")
                return func(user, *args, **kwargs)

            except ValueError as exc:
                # This will be raised if the token is expired or any other
                # verification checks fail.
                error_message = str(exc)
                logging.error(f"ERROR: {error_message} {request.method} {request.url} {func.__name__}")
        else:
            logging.info(f"{request.method} {request.url} {func.__name__} <no-user>->/login/")
            return redirect('/login/')

    return wrapper


########## user store ##########

# TODO: this needs to be moved to a memory cache (Redis?).
# a new instance could be spun up with no shared memory =empty user_cache var
# user_cache[id_token] = user
user_cache = {} # TODO: memcache the users to avoid parsing the session cookie every request

def get_user(id_token: str) -> ScoutnetUser:
    if id_token not in user_cache:
        return None
    return user_cache[id_token]

def add_user(id_token: str, user: ScoutnetUser) -> None:
    user_cache[id_token] = user
    # TODO:
    # key = hashlib.md5(id_token).hexdigest()
    # memcache.replace(key, user) # not sure this will work, maybe the user will be pickled

def login_user_from_id_token(id_token: str) -> ScoutnetUser:
    firebase_request_adapter = requests.Request()
    claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
    user_data = claims['firebase']['sign_in_attributes']
    user = parse_and_add_user(id_token, user_data)
    return user

def parse_roles(roles):
    """
    Example json:
    {"organisation":{"692":{"235":"scoutid_admin","442":"7746c8"}},
	"region":[],
	"project":[],
	"network":[],
	"corps":[],
	"district":[],
	"group":
	  {
		"1137":{
		  "9":"member_registrar",
		  "15":"board_member",
		  "36":"webmaster"
		}
	  },
	  "troop":
	  {
		"20059":{"2":"leader"}
	  },
	  "patrol":[]
	  }
    """
    # if this is a string we need to parse the json, else assume it's already parsed
    if isinstance(roles, str):
        return json.loads(roles)

    return roles


def parse_user(user_data) -> ScoutnetUser:
    print(user_data)
    email = user_data['email']
    group_no = user_data['group_no']
    group_id = user_data['group_id']
    uid = user_data['uid']
    displayName = user_data['displayName']
    member_registrar = False
    if 'roles' in user_data:
        roles = parse_roles(user_data['roles']) # this is a json string (must be a bug in scoutid)
        if 'group' in roles:
            group = roles['group']
            if str(group_id) in group:
                group_id_roles = group[str(group_id)]
                member_registrar = '9' in group_id_roles # member_registrar

    user = ScoutnetUser(displayName, email, uid, group_no, group_id, member_registrar)
    logging.info(f"User: {user.getname()}, {user.email}")
    return user


def parse_and_add_user(id_token: str, user_data) -> ScoutnetUser:
    user = parse_user(user_data)
    if not user:
        return None
    add_user(id_token, user)
    return user
