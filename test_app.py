import unittest
import meep_example_app
import socket
import urllib

class TestApp(unittest.TestCase):
    def setDefaults(self):
        self.ux = 'foo'
        self.px = 'bar'
        e = {}                    # make a fake dict
        e['REQUEST_METHOD'] = 'GET'
        e['SCRIPT_NAME'] = ''
        e['QUERY_STRING'] = ''
        e['CONTENT_TYPE'] = 'text/plain'
        e['CONTENT_LENGTH'] = '0'
        e['SERVER_NAME'] = socket.gethostbyaddr("127.0.0.1")[0]
        e['SERVER_PORT'] = '8000'
        e['SERVER_PROTOCOL'] = 'HTTP/1.1'
        self.environ = e
        
    def setUp(self):
    	print '\n\n\n\n'
        app = meep_example_app.MeepExampleApp()
        self.app = app
        self.setDefaults()

    def create_test_user(self):
        print ''
        print 'CREATING USER'
        print ''
        self.setDefaults()
        self.environ['PATH_INFO'] = '/create_user'
        self.environ['wsgi.input'] = ''
        form_dict = {}
        form_dict['username'] = self.ux
        form_dict['password'] = self.px
        form_dict['password_confirm'] = self.px
        self.environ['QUERY_STRING'] = urllib.urlencode(form_dict)
        
        def fake_start_response2(status, headers):
            assert status == '302 Found'
            assert ('Set-Cookie', 'username=%s; Path=/' % (self.ux,)) in headers

        data = self.app(self.environ, fake_start_response2)
    

    def test_PageShows_Index_LoggedOut(self):
        print ''
        print 'STARTING test_PageShows_Index_LoggedOut'
        self.environ['PATH_INFO'] = '/'

        def fake_start_response(status, headers):
            assert status == '200 OK'
            assert ('Content-type', 'text/html') in headers

        data = self.app(self.environ, fake_start_response)
        assert 'Create a New User' in data[0]
        assert 'Show messages' in data[0]
        
        print 'ENDING test_PageShows_Index_LoggedOut'
        print ''

    def test_PageShows_Index_LoggedIn(self):
        print ''
        print 'STARTING test_PageShows_Index_LoggedIn'
        
        self.create_test_user()
        self.setDefaults()
        """
        self.environ['PATH_INFO'] ='/'
        self.environ['HTTP_COOKIE'] = "username=%s" % (self.ux,)
       
        def fake_start_response(status, headers):
            assert status == '200 OK'
            assert ('Content-type', 'text/html') in headers

        data = self.app(self.environ, fake_start_response)
        print 'data printing'
        print data[0]
        assert 'you are logged in as user: test.' in data[0]
        assert 'Show messages' in data[0]
        """
        print 'ENDING test_PageShows_Index_LoggedIn'
        print ''

    def test_PageShows_CreateUser_LoggedOut(self):
        print ''
        print 'STARTING test_PageShows_CreateUser_LoggedOut'
        self.environ['PATH_INFO'] ='/create_user'
        self.environ['wsgi.input'] = ''
        def fake_start_response(status, headers):
            assert status == '200 OK'
            assert ('Content-type', 'text/html') in headers

        data = self.app(self.environ, fake_start_response)
        assert 'username:' in data[0]
        assert 'password:' in data[0]
        assert 'confirm password:' in data[0]
        
        print 'ENDING test_PageShows_CreateUser_LoggedOut'
        print ''

    def test_PageShows_Login(self):
        print ''
        print 'STARTING test_PageShows_Login'
        self.environ['PATH_INFO'] ='/login'
        self.environ['wsgi.input'] = ''
        def fake_start_response(status, headers):
            assert status == '302 Found'
            assert ('Content-type', 'text/html') in headers

        data = self.app(self.environ, fake_start_response)
        assert 'Or Create a New User' in data[0]
        assert 'username' in data[0]
        assert 'password' in data[0]
        
        print 'ENDING test_PageShows_Login'
        print ''

    def test_PageShows_ShowMessages_LoggedOut(self):
        print ''
        print 'STARTING test_PageShows_ShowMessages_LoggedOut'
        self.environ['PATH_INFO'] ='/m/list'
        self.environ['wsgi.input'] = ''
        def fake_start_response(status, headers):
             assert status == '200 OK'
             assert ('Content-type', 'text/html') in headers

        data = self.app(self.environ, fake_start_response)
        assert '''Hayden Boroski's Message Board''' in data[0]
        
        #verify reply buttons are hidden.
        assert '''class="messageReply hidden"''' in data[0]
        
        print 'ENDING test_PageShows_ShowMessages_LoggedOut'
        print ''

    def test_PageShows_ShowMessages_LoggedIn(self):
        print ''
        print 'STARTING test_PageShows_ShowMessages_LoggedIn'
        self.environ['PATH_INFO'] ='/m/list'
        self.environ['HTTP_COOKIE'] = "username=%s" % (self.ux,)
        self.environ['wsgi.input'] = ''
        def fake_start_response(status, headers):
             assert status == '200 OK'
             assert ('Content-type', 'text/html') in headers

        data = self.app(self.environ, fake_start_response)
        assert '''Hayden Boroski's Message Board''' in data[0]
        
        #verify reply buttons are hidden.
        assert '''class="messageReply hidden"''' in data[0]
        
        print 'ENDING test_PageShows_ShowMessages_LoggedIn'
        print ''
        

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()