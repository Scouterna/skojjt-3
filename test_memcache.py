import unittest
from memcache import memcache
from scoutnetuser import ScoutnetUser


class TestMemcache(unittest.TestCase):

    def testMemcacheGetSet(self):
        # TODO: test code move to test file
        memcache.set("TestKey", "TestData")
        assert(memcache.get("TestKey") == b"TestData")

    def testMemcachePickled(self):
        testuser = ScoutnetUser("Test User", "abc@xyz.qwe", 1111, {})
        memcache.set_pickled("testuser", testuser)
        unpickled_testuser = memcache.get_unpickled("testuser")
        assert(unpickled_testuser.getname() == testuser.getname())
        assert(unpickled_testuser.email == testuser.email)
        assert(unpickled_testuser.uid == testuser.uid)


if __name__ == '__main__':
    unittest.main()