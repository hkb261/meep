import unittest
import meep_example_app
import twill

class TestMeepLib(unittest.TestCase):

    def setUp(self):
        pass

    def test_01_create_user(self):
        twill.execute_file("tests/01CreateUser.twill", initial_url="http://localhost:8000")

    def test_02_add_message(self):
        twill.execute_file("tests/02AddMessage.twill", initial_url="http://localhost:8000")

    def test_03_reply_message(self):
        twill.execute_file("tests/03ReplyMessage.twill", initial_url="http://localhost:8000")

    def test_04_delete_message(self):
        twill.execute_file("tests/04DeleteMessage.twill", initial_url="http://localhost:8000")

    def test_05_confirm_sequence(self):
        twill.execute_file("tests/05ConfirmLoginLogoutSequence.twill", initial_url="http://localhost:8000")

    def test_06_delete_test_user(self):
        #this isn't actually a test. it's simply to clean up after ourselves.
        e = {}
        e['REQUEST_METHOD'] = 'GET'
        e['SCRIPT_NAME'] = ''
        e['QUERY_STRING'] = ''
        e['CONTENT_TYPE'] = 'text/plain'
        e['CONTENT_LENGTH'] = '0'
        e['SERVER_NAME'] = 'localhost'
        e['SERVER_PORT'] = '8000'
        e['SERVER_PROTOCOL'] = 'HTTP/1.1'
        e['HTTP_COOKIE'] = "username=twillTester"
        
        app = meep_example_app.MeepExampleApp()
        def fake_start_response(status, headers):
            pass
        app.delete_loggedin_user_action(e, fake_start_response)  

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
