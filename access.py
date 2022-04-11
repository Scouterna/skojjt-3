import logging
from xmlrpc.client import Boolean
#from data import UserPrefs
from data import Semester
from flask import request, render_template, redirect
from functools import wraps
from google.auth.transport import requests
import google.oauth2.id_token
import os
from scoutnetuser import ScoutnetUser


def login():
    # Verify Firebase auth.
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None
    user_data = None

    if id_token:
        try:
            # Verify the token against the Firebase Auth API. This example
            # verifies the token on each page load. For improved performance,
            # some applications may wish to cache results in an encrypted
            # session store (see for instance
            # http://flask.pocoo.org/docs/1.0/quickstart/#sessions).
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)

            user_data = claims['firebase']['sign_in_attributes']
            # print(user_data)
            email = user_data['email']

            store_time(email, datetime.datetime.now())
            times = fetch_times(email, 10)

        except ValueError as exc:
            # This will be raised if the token is expired or any other
            # verification checks fail.
            error_message = str(exc)

    return render_template(
        'login.html',
        user_data=user_data, error_message=error_message, times=times)



def checkAccess(func):
    '''
    Decorator for access check.
    Parameters:
        func: is the function to be decorator it needs to take a ScoutnetUser as first argument, func(user, *args, **kwargs)
    '''

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Verify Firebase auth.
        id_token = request.cookies.get("token")
        error_message = None
        claims = None
        times = None
        user_data = None
        user_cache = {} # TODO: memcache the users to avoid parsing the session cookie every request
        if id_token:
            try:
                # Verify the token against the Firebase Auth API. This example
                # verifies the token on each page load. For improved performance,
                # some applications may wish to cache results in an encrypted
                # session store (see for instance
                # http://flask.pocoo.org/docs/1.0/quickstart/#sessions).
                if id_token not in user_cache:
                    firebase_request_adapter = requests.Request()
                    claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)

                    user_data = claims['firebase']['sign_in_attributes']
                    # print(user_data)
                    email = user_data['email']
                    group_no = user_data['group_no']
                    group_id = user_data['group_id']
                    uid = user_data['uid']
                    displayName = user_data['displayName']
                    member_registrar = False
                    if 'roles' in user_data:
                        roles = user_data['roles']
                        if 'group' in roles:
                            group = roles['group']
                            if str(group_id) in group:
                                group_id_roles = group[str(group_id)]
                                member_registrar = '9' in group_id_roles # member_registrar
                    user = ScoutnetUser(displayName, email, uid, group_no, group_id, member_registrar) #parse_access(email) # TODO:
                    user_cache[id_token] = user
                else:
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

