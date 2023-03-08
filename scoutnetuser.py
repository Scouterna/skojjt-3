from data import Semester
import logging
import json


class ScoutnetUser():
    def __init__(self, display_name: str, email: str, uid: str, group_roles: dict[str, str]):
        self.display_name = display_name
        self.email = email
        self.uid = uid
        self.group_roles = group_roles
        self.active_semester = None # TODO: set active semester

    def getname(self) -> str:
        return self.display_name

    def hasAccess(self, group_id) -> bool:
        return self.hasOneOfRoles(group_id, ["leader", "member_registrar"])
    
    def isGroupAdmin(self, group_id: str) -> bool:
        return self.hasOneOfRoles(group_id, ["member_registrar"])

    def canImport(self, group_id) -> bool:
        return self.hasOneOfRoles(group_id, ["member_registrar"])

    def getActiveSemester(self) -> Semester:
        return self.active_semester

    def isSuperUser(self) -> bool:
        # TODO: fetch scoutnet id (uid) from a table with super users.
        return False

    def getAllGroupIds(self) -> list[str]:
        return [group_id for group_id in self.group_roles]

    def hasOneOfRoles(self, group_id: str, desired_roles: list[str]):
        if group_id not in self.group_roles:
            return False
        roles = self.group_roles[group_id]
        for role_id in roles:
            if roles[role_id] in desired_roles:
                return True
        return False

    @staticmethod
    def loads_json_if_string(data):
        # if this is a string we need to parse the json, else assume it's already parsed
        if isinstance(data, str):
            return json.loads(data)
        return data

    @staticmethod
    def parse_user(user_data) -> "ScoutnetUser":
        print(user_data)
        email = user_data['email']
        # these can be an array of groups if you are member of multiple groups
        #group_no = user_data['group_no']
        #group_id = user_data['group_id']
        uid = user_data['uid']
        display_name = user_data['displayName']
        group_roles = []
        if 'roles' in user_data:
            roles = ScoutnetUser.loads_json_if_string(user_data['roles']) # this is a json string (must be a bug in scoutid)
            if 'group' in roles:
                # Assuming here that if you are leader in multiple groups you will get a role on each group having an array of groups with roles
                # yet to be verified.
                group_roles = roles['group']

        user = ScoutnetUser(display_name, email, uid, group_roles)
        logging.info(f"User: {user.getname()}, {user.email}")
        return user

    @property
    def activeSemester(self):
        return self.active_semester
    
    @activeSemester.setter
    def activeSemester(self, value):
        self.active_semester = value

    @property
    def key(self) -> str:
        return self.uid

    def put(self):
        pass # TODO: store active_semester in db
