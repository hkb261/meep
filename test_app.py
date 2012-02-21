import unittest
import meep_example_app
import socket
import urllib

class TestApp(unittest.TestCase):
    def setDefaults(self):
        self.ux = 'foo'
        self.px = 'bar'
        self.msgTitle = 'Test Message Title'
        self.msgPost = 'Test Message Post'
        self.msgReply = 'Test Message Reply'
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
        app = meep_example_app.MeepExampleApp()
        self.app = app
        self.setDefaults()

    def test_00_PageShows_Index_LoggedOut(self):
        self.environ['PATH_INFO'] = '/'

        def fake_start_response(status, headers):
            assert status == '200 OK'
            assert ('Content-type', 'text/html') in headers

        data = self.app(self.environ, fake_start_response)
        assert 'Not Registered?' in data[0]
        assert '<a href="/login">Log In</a>' in data[0]
        

    def test_01_PageShows_CreateUser_LoggedOut(self):
        self.environ['PATH_INFO'] ='/create_user'
        self.environ['wsgi.input'] = ''
        def fake_start_response(status, headers):
            assert status == '200 OK'
            assert ('Content-type', 'text/html') in headers

        data = self.app(self.environ, fake_start_response)
        assert 'User Name:' in data[0]
        assert 'Password:' in data[0]
        assert 'Confirm Password:' in data[0]

    def test_02_PageShows_Login_LoggedOut(self):
        self.environ['PATH_INFO'] ='/login'
        self.environ['wsgi.input'] = ''
        def fake_start_response(status, headers):
            assert status == '200 OK'
            assert ('Content-type', 'text/html') in headers

        data = self.app(self.environ, fake_start_response)
        assert 'User Name:' in data[0]
        assert 'Password:' in data[0]

    def test_03_Create_User(self):
        self.setDefaults()
        self.environ['PATH_INFO'] = '/create_user'
        self.environ['wsgi.input'] = ''
        form_dict = {}
        form_dict['username'] = self.ux
        form_dict['password'] = self.px
        form_dict['password_confirm'] = self.px
        self.environ['QUERY_STRING'] = urllib.urlencode(form_dict)
        
        def fake_start_response(status, headers):
            assert status == '302 Found'
            assert ('Set-Cookie', 'username=%s; Path=/' % (self.ux,)) in headers

        data = self.app(self.environ, fake_start_response)


    def test_04_Add_Message(self):
        self.environ['PATH_INFO'] ='/m/add_action'
        self.environ['HTTP_COOKIE'] = "username=%s" % (self.ux,)
        self.environ['wsgi.input'] = ''
        form_dict = {}
        form_dict['title'] = self.msgTitle
        form_dict['message'] = self.msgPost
        self.environ['QUERY_STRING'] = urllib.urlencode(form_dict)
        
        def fake_start_response(status, headers):
            assert status == '302 Found'

        data = self.app(self.environ, fake_start_response)
    
    def test_05_PageShows_ShowMessages_LoggedIn(self):
        self.environ['PATH_INFO'] ='/'
        self.environ['HTTP_COOKIE'] = "username=%s" % (self.ux,)
        self.environ['wsgi.input'] = ''
        def fake_start_response(status, headers):
             assert status == '200 OK'
             assert ('Content-type', 'text/html') in headers

        data = self.app(self.environ, fake_start_response)
        assert '''Hayden Boroski's Message Board''' in data[0]
        
        assert """<input type='submit' id='bttnDelete'"""  in data[0]

	def test_06_Delete_Message(self):
	    self.environ['PATH_INFO'] ='/'
        self.environ['HTTP_COOKIE'] = "username=%s" % (self.ux,)
        self.environ['wsgi.input'] = ''
        def fake_start_response(status, headers):
             assert status == '200 OK'
             assert ('Content-type', 'text/html') in headers
             
    	data = self.app(self.environ, fake_start_response)
    	
    	assert self.msgTitle in data[0]
    	assert self.msgPost in data[0]
    	
    	html = data[0]
    	location = html.find(self.msgTitle)
    	idstart = html.find("name='id' value='",location)
    	id = html[idstart + 17:]
    	id = id[:id.find("'")]    	
    	self.setDefaults()
    	self.msgId = id

        self.environ['PATH_INFO'] ='/m/alterMessage'
        self.environ['HTTP_COOKIE'] = "username=%s" % (self.ux,)
        self.environ['wsgi.input'] = ''
        form_dict = {}
        form_dict['id'] = self.msgId
        form_dict['bttnSubmit'] = 'Delete'
        self.environ['QUERY_STRING'] = urllib.urlencode(form_dict)
        
        def fake_start_response(status, headers):
            assert status == '302 Found'
    	
    	data = self.app(self.environ, fake_start_response)
	
	
    def test_07_Delete_user(self):
        self.environ['HTTP_COOKIE'] = "username=%s" % (self.ux,)
        def fake_start_response(status, headers):
            pass
        self.app.delete_loggedin_user_action(self.environ, fake_start_response)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()