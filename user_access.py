import logging
from flask import request, redirect, make_response, url_for
from functools import wraps
import usersessions


def user_access(func):
    '''
    Decorator for access check.
    Parameters:
        func: is the function to be decorator it needs to take a ScoutnetUser as first argument, func(user, *args, **kwargs)
    '''

    @wraps(func)
    def wrapper(*args, **kwargs):
        #logging.info(f"{request.method} {request.url} {func.__name__} user_access wrapper")
        session_id = request.cookies.get("session_id")
        if session_id:
            user = usersessions.get_user_from_session_id(session_id)
            if user:
                logging.info(f"{request.method} {request.url} {func.__name__} uid:{user.uid}")
                return func(user, *args, **kwargs)

        logging.info(f"{request.method} {request.url} {func.__name__} <no-user>->/login/")
        response = make_response(redirect(url_for("login")))
        response.set_cookie("after_login_url", request.url)
        return response

    return wrapper

