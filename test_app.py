import unittest
import meep_example_app

class TestApp(unittest.TestCase):
    def setUp(self):
        app = meep_example_app.MeepExampleApp()
        self.app = app

    def test_PageShows_Index_LoggedOut(self):
        environ = {}                    # make a fake dict
        environ['PATH_INFO'] = '/'

        def fake_start_response(status, headers):
            assert status == '200 OK'
            assert ('Content-type', 'text/html') in headers

        data = self.app(environ, fake_start_response)
        assert 'Create a New User' in data[0]
        assert 'Show messages' in data[0]

    def test_PageShows_Index_LoggedIn(self):
        environ = {}
        environ['PATH_INFO'] ='/'
        environ['HTTP_COOKIE'] = "username=test"
       
        def fake_start_response(status, headers):
            assert status == '200 OK'
            assert ('Content-type', 'text/html') in headers

        data = self.app(environ, fake_start_response)
        print 'data printing'
        print data[0]
        assert 'you are logged in as user: test.' in data[0]
        assert 'Show messages' in data[0]

    def test_PageShows_CreateUser_LoggedOut(self):
       environ = {}
       environ['PATH_INFO'] ='/create_user'
       environ['wsgi.input'] = ''
       def fake_start_response(status, headers):
            assert status == '302 Found'
            assert ('Content-type', 'text/html') in headers

       data = self.app(environ, fake_start_response)
       assert 'username:' in data[0]
       assert 'password:' in data[0]
       assert 'confirm password:' in data[0]

    def test_PageShows_Login(self):
       environ = {}
       environ['PATH_INFO'] ='/login'
       environ['wsgi.input'] = ''
       def fake_start_response(status, headers):
            assert status == '302 Found'
            assert ('Content-type', 'text/html') in headers

       data = self.app(environ, fake_start_response)
       assert 'Or Create a New User' in data[0]
       assert 'username' in data[0]
       assert 'password' in data[0]

    def test_PageShows_ShowMessages_LoggedOut(self):
        environ = {}
        environ['PATH_INFO'] ='/m/list'
        environ['wsgi.input'] = ''
        def fake_start_response(status, headers):
             assert status == '200 OK'
             assert ('Content-type', 'text/html') in headers

        data = self.app(environ, fake_start_response)
        assert '''Hayden Boroski's Message Board''' in data[0]
        
        #verify reply buttons are hidden.
        assert '''class="messageReply hidden"''' in data[0]

    def test_PageShows_ShowMessages_LoggedIn(self):
        environ = {}
        environ['PATH_INFO'] ='/m/list'
        environ['HTTP_COOKIE'] = "username=test"
        environ['wsgi.input'] = ''
        def fake_start_response(status, headers):
             assert status == '200 OK'
             assert ('Content-type', 'text/html') in headers

        data = self.app(environ, fake_start_response)
        assert '''Hayden Boroski's Message Board''' in data[0]
        
        #verify reply buttons are hidden.
        assert '''class="messageReply hidden"''' in data[0]
        

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()