import unittest
import meeplib

# note:
#
# functions start within test_ are discovered and run
#       between setUp and tearDown;
# setUp and tearDown are run *once* for *each* test_ function.

class TestMeepLib(unittest.TestCase):
    
    def setUp(self):
        self.ux = 'foo'
        self.px = 'bar'
        self.msgTitle = 'the title'
        self.msgMsg = 'the content'
        u = meeplib.User(self.ux, self.px)
        m = meeplib.Message(self.msgTitle, self.msgMsg, u)
        self.msgId = m.id

    def test_for_message_existence(self):
        assert meeplib.get_message(self.msgId) != None

    def test_user_existence(self):
        assert meeplib.get_user(self.ux) != None

    def test_message_ownership(self):
        assert meeplib.get_message(self.msgId).author == meeplib.get_user(self.ux)
    
    def test_add_reply(self):
        msg = meeplib.get_message(self.msgId)
        new_message = meeplib.Message('reply', 'reply msg',  msg.author, True)
        msg.add_reply(new_message)
        
        replies = msg.get_replies()
        assert len(replies) == 1
        
    def test_delete_message(self):
        msg = meeplib.get_message(self.msgId)
        meeplib.delete_message(msg)
        
        print (meeplib.get_message(self.msgId),)
        assert meeplib.get_message(self.msgId) == None

    def tearDown(self):
        m = meeplib.get_message(self.msgId)
        if m != None:
            meeplib.delete_message(m)
            

        l = len(meeplib.get_all_users())
        meeplib.delete_user(meeplib.get_user(self.ux))
        lafter = len(meeplib.get_all_users())
        
        assert l > lafter

if __name__ == '__main__':
    unittest.main()
