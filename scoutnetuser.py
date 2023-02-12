from data import Semester


class ScoutnetUser():
    def __init__(self, displayName: str, email: str, uid: int, group_no: int, group_id: int, member_registrar: bool):
        self.displayName = displayName
        self.email = email
        self.uid = uid
        self.group_no = group_no
        self.group_id = group_id
        self.member_registrar = member_registrar
        # self.activeSemester = Semester.getOrCreateCurrent() # TODO: read/write from database
        self.activeSemester = None

    def getname(self) -> str:
        return self.displayName

    def hasAccess(self) -> bool:
        return self.group_id != 0
    
    def isGroupAdmin(self) -> bool:
        return self.member_registrar

    def canImport(self) -> bool:
        return self.member_registrar

    def getActiveSemester(self) -> Semester:
        return self.activeSemester

    def isSuperUser(self) -> bool:
        # TODO: fetch scoutnet id (uid) from a table with super users.
        return False
