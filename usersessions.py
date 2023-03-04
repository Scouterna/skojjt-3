from datetime import datetime, timedelta
import logging
from xmlrpc.client import Boolean
from google.auth.transport import requests
import google.oauth2.id_token
from scoutnetuser import ScoutnetUser
from memcache import memcache


class UserSessionEntry():
    def __init__(self, user: ScoutnetUser, expires: datetime):
        self.user = user
        self.expires = expires # TODO: update expire time
    
    def get_expire_seconds_from_now(self) -> int:
        return max(int((self.expires-datetime.utcnow()).total_seconds()), 0)

    def extend_expire(self) -> None:
        self.expires = datetime.utcnow() + timedelta(hours=2)

    def is_expired(self) -> Boolean:
        return datetime.utcnow() > self.expires



local_user_cache: dict[str, UserSessionEntry] = {}

def get_user_from_session_id(session_id: str) -> ScoutnetUser:
    key = session_id
    if key in local_user_cache:
        user_session_entry = local_user_cache[key]
    else:
        user_session_entry = memcache.get_unpickled(key)

    if user_session_entry:
        if user_session_entry.is_expired():
            logging.info(f"User session expired {user_session_entry.expires}, uid:{user_session_entry.user.uid}")
            memcache.remove(key)
            if key in local_user_cache:
                del local_user_cache[key]
            return None
        else:
            user_session_entry.extend_expire()
            memcache.set_expire(key, user_session_entry.get_expire_seconds_from_now())
            return user_session_entry.user

def add_user_session(subject_identifier: str, expires: datetime, user: ScoutnetUser) -> None:
    user_session_entry = UserSessionEntry(user, expires)
    key = subject_identifier
    local_user_cache[key] = user_session_entry
    memcache.replace_picked(key, user_session_entry, user_session_entry.get_expire_seconds_from_now())

def remove_user_session(subject_identifier:str) -> None:
    key = subject_identifier
    if key in local_user_cache:
        del local_user_cache[key]
    memcache.remove(key)

def login_user_from_id_token(id_token: str) -> tuple[ScoutnetUser, str]:
    firebase_request_adapter = requests.Request()
    claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
    subject_identifier = claims['sub'] # using this as session id, to avoid having to parse the whole token every time
    expires_rfc3339 = claims['exp'] # Expire time for session (rfc3339), i.g. 1677582939 :int
    expires = datetime.fromtimestamp(expires_rfc3339)
    user_data = claims['firebase']['sign_in_attributes']
    user = parse_and_add_user(subject_identifier, expires, user_data)
    return (user, subject_identifier)

def parse_and_add_user(subject_identifier: str, expires: datetime, user_data) -> ScoutnetUser:
    user = ScoutnetUser.parse_user(user_data)
    if not user:
        return None
    add_user_session(subject_identifier, expires, user)
    return user