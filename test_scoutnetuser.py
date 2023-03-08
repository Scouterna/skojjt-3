import unittest
from memcache import memcache
from scoutnetuser import ScoutnetUser
import json


class TestScoutnetUser(unittest.TestCase):

    def testDefaultScoutnetUser(self):
        testuser = ScoutnetUser("Test User", "abc@xyz.qwe", 1234, {})
        assert(testuser.getname() == "Test User")
        assert(testuser.email == "abc@xyz.qwe")
        assert(testuser.uid == 1234)
        assert(testuser.key == 1234)
        assert(testuser.getAllGroupIds() == [])

    def testSingleMemberScoutnetUser(self):
        # single membership, leader in one group
        roles = json.loads('{"1137":{"6":"leader"}}')
        testuser = ScoutnetUser("Test User", "abc@xyz.qwe", 1234, roles)
        assert(testuser.getname() == "Test User")
        assert(testuser.email == "abc@xyz.qwe")
        assert(testuser.uid == 1234)
        group_ids = testuser.getAllGroupIds()
        assert(len(group_ids) == 1)
        assert("1137" in group_ids)
        assert(testuser.hasAccess("1137") == True)
        assert(testuser.canImport("1137") == False)
        assert(testuser.isGroupAdmin("1137") == False)
        assert(testuser.isSuperUser() == False)

    def testDoubleMemberScoutnetUser(self):
        # multiple membership, leader in two groups            
        roles = json.loads('{ "1137":{"6":"leader","9":"member_registrar"},"1126":{"6":"leader"} }')
        testuser = ScoutnetUser("Test User", "abc@xyz.qwe", 1234, roles)
        assert(testuser.getname() == "Test User")
        assert(testuser.email == "abc@xyz.qwe")
        assert(testuser.uid == 1234)
        group_ids = testuser.getAllGroupIds()
        assert(len(group_ids) == 2)
        assert("1126" in group_ids)
        assert("1137" in group_ids)
        assert(testuser.hasAccess("1126") == True)
        assert(testuser.hasAccess("1137") == True)
        assert(testuser.canImport("1137") == True)
        assert(testuser.canImport("1126") == False)
        assert(testuser.isGroupAdmin("1137") == True)
        assert(testuser.isGroupAdmin("1126") == False)
        assert(testuser.isSuperUser() == False)


    def testParseUserMemberScoutnetUser1(self):
        test_user1 = """{'sub': '123456789@scoutnet.se', 'firstname': 'Test1', 'role': ['*:*:7746c8', '*:*:board_member', '*:*:leader', '*:*:member_registrar', '*:*:scoutid_admin', '*:*:webmaster', 'group:*:*', 'group:*:board_member', 'group:*:member_registrar', 'group:*:webmaster', 'group:1137:*', 'group:1137:board_member', 'group:1137:member_registrar', 'group:1137:webmaster', 'organisation:*:*', 'organisation:*:7746c8', 'organisation:*:scoutid_admin', 'organisation:692:*', 'organisation:692:7746c8', 'organisation:692:scoutid_admin', 'troop:*:*', 'troop:*:leader', 'troop:20059:*', 'troop:20059:leader'], 'group_name': 'Tynnereds Scoutkår', 'displayName': 'Test1 Efternamn1', 'roles': '{"organisation":{"692":{"235":"scoutid_admin","442":"7746c8"}},"region":[],"project":[],"network":[],"corps":[],"district":[],"group":{"1137":{"9":"member_registrar","15":"board_member","36":"webmaster"}},"troop":{"20059":{"2":"leader"}},"patrol":[]}', 'above_15': '1', 'lastname': 'Efternamn1', 'group_no': '32048', 'uid': '123456789', 'group_id': '1137', 'dob': '1907-01-24', 'email': 'Test1@testserver.se', 'firstlast': 'Test1.Efternamn1'}"""
        testuser = ScoutnetUser.parse_user(json.loads(test_user1.replace('"', '\\"').replace("'", '"')))
        assert(testuser.getname() == "Test1 Efternamn1")
        assert(testuser.email == "Test1@testserver.se")
        assert(testuser.uid == '123456789')
        group_ids = testuser.getAllGroupIds()
        assert(len(group_ids) == 1)
        assert("1137" in group_ids)
        assert(testuser.hasAccess("1137") == True)
        assert(testuser.canImport("1137") == True)
        assert(testuser.isGroupAdmin("1137") == True)


    def testParseUserMemberScoutnetUser2(self):
        test_user2 = """{"sub": "987654321@scoutnet.se", "firstname": "Test2", "role": ["*:*:company_signatory", "*:*:leader", "*:*:member_registrar", "*:*:other_leader", "*:*:police_check_admin", "*:*:project_admin", "*:*:vice_leader", "*:*:webmaster", "group:*:*", "group:*:company_signatory", "group:*:leader", "group:*:member_registrar", "group:*:police_check_admin", "group:*:webmaster", "group:1137:*", "group:1137:company_signatory", "group:1137:leader", "group:1137:member_registrar", "group:1137:police_check_admin", "group:1137:webmaster", "project:*:*", "project:*:leader", "project:*:project_admin", "project:3184:*", "project:3184:leader", "project:3184:project_admin", "troop:*:*", "troop:*:leader", "troop:*:other_leader", "troop:*:vice_leader", "troop:16763:*", "troop:16763:other_leader", "troop:16763:vice_leader", "troop:19171:*", "troop:19171:leader"], "group_name": ["Masthugget Majornas Scoutk\\u00e5r", "Tynnereds Scoutk\\u00e5r"], "displayName": "Test2 Efternamn2", "roles": "{\\"organisation\\":[],\\"region\\":[],\\"project\\":{\\"3184\\":{\\"65\\":\\"leader\\",\\"138\\":\\"project_admin\\"}},\\"network\\":[],\\"corps\\":[],\\"district\\":[],\\"group\\":{\\"1137\\":{\\"36\\":\\"webmaster\\",\\"6\\":\\"leader\\",\\"9\\":\\"member_registrar\\",\\"49\\":\\"company_signatory\\",\\"1238\\":\\"police_check_admin\\"}},\\"troop\\":{\\"16763\\":{\\"3\\":\\"other_leader\\",\\"4\\":\\"vice_leader\\"},\\"19171\\":{\\"2\\":\\"leader\\"}},\\"patrol\\":[]}", "above_15": "1", "lastname": "Efternamn2", "group_no": ["32028", "32048"], "uid": "987654321", "group_id": ["1126", "1137"], "dob": "1909-07-30", "email": "Test2@testserver.se", "firstlast": "Test2.Efternamn2"}"""
        testuser = ScoutnetUser.parse_user(json.loads(test_user2))
        assert(testuser.getname() == "Test2 Efternamn2")
        assert(testuser.email == "Test2@testserver.se")
        assert(testuser.uid == '987654321')
        group_ids = testuser.getAllGroupIds()
        assert(len(group_ids) == 1)
        assert("1137" in group_ids)
        assert(testuser.hasAccess("1137") == True)
        assert(testuser.canImport("1137") == True)
        assert(testuser.isGroupAdmin("1137") == True)


if __name__ == '__main__':
    unittest.main()