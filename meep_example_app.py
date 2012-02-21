import meeplib
import traceback
import cgi
import meepcookie
from cgi import parse_qs, escape
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('templates'))

def render_page(filename, **variables):
    template = env.get_template(filename)
    x = template.render(**variables)
    return str(x)

class MeepExampleApp(object):
    """
    WSGI app object.
    """
    def __init__(self):
        meeplib.initialize()
    
    def getUser(self, environ):
        username = meepcookie.get_cookie_value(environ,'username')
        user = None
        if username != '':
            user = meeplib.get_user(username)
        return user
    
    def log_user_in(self, environ, headers, username):
        cookie_name, cookie_val = \
            meepcookie.make_set_cookie_header('username', username)
        headers.append((cookie_name, cookie_val))
        
    def log_user_out(self, environ, headers):
        cookie_name, cookie_val = \
            meepcookie.delete_cookie(environ, 'username')
        headers.append((cookie_name, cookie_val))
        
    def get_value(self, form, isPost, key, default):
        retVal = ''
        try:
            if isPost:
                retVal = form[key].value
            else:
                retVal = form.get(key,'')[0]
        except:
            retVal = default

        return retVal
        
    def index(self, environ, start_response):
        headers = [('Content-type', 'text/html')]
        start_response('200 OK', headers)
        return [render_page('index.html', user=self.getUser(environ), \
        	messages=meeplib.get_all_messages())]

    def login(self, environ, start_response):
        headers = [('Content-type', 'text/html')]

        post = (environ.get('REQUEST_METHOD') == 'POST')
        #if post:
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
        #else:
        #    form = parse_qs(environ['QUERY_STRING'])
	
        username = self.get_value(form,post,'username','')
        password = self.get_value(form,post,'password','')
        
        s=[]

        err = False
        if username != '' and password != '':
            user = meeplib.get_user(username)
            if user is not None and user.password == password:
                self.log_user_in(environ, headers, user.username)
                k = 'Location'
                v = '/'
                headers.append((k, v))
                start_response('302 Found', headers)
                return []
            elif user is None:
                err = True
            else:
                err = True
        elif username != '' or password != '':
            err = True

        if post:
            err = True

        start_response('200 OK', headers)
        return [render_page('login.html', error=err)]

    def logout(self, environ, start_response):

        headers = [('Content-type', 'text/html')]
        self.log_user_out(environ, headers)
        # send back a redirect to '/'
        k = 'Location'
        v = '/'
        headers.append((k, v))
        start_response('302 Found', headers)
        return "no such content"

    def create_user(self, environ, start_response):
        headers = [('Content-type', 'text/html')]

        post = (environ.get('REQUEST_METHOD') == 'POST')
        if post:
        	form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
        else:
            form = parse_qs(environ['QUERY_STRING'])
	
        username = self.get_value(form,post,'username','')
        password = self.get_value(form,post,'password','')
        password2 = self.get_value(form,post,'password_confirm','')
        
        s=[]
        
        ##if we have username and password and confirmation password
        err = False
        if username != '':
            user = meeplib.get_user(username)
            ## user already exists
            if user is not None:
                err = True
            ## user doesn't exist but they messed up the passwords
            elif password == '':
                err = True
            elif password != password2:
                err = True
            else:
                u = meeplib.User(username, password)
                ## send back a redirect to '/'
                k = 'Location'
                v = '/'
                headers.append((k, v))
                self.log_user_in(environ, headers, u.username)
                start_response('302 Found', headers)
                return []
        elif password != '' or password2 != '':
                err = True
                
        if post:
        	err = True
        	
        headers = [('Content-type', 'text/html')]
        start_response('200 OK', headers)
        return [render_page('createUser.html', error=err)]

    def alter_message_action(self, environ, start_response):
        post = (environ.get('REQUEST_METHOD') == 'POST')
        if post:
        	form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
        else:
            form = parse_qs(environ['QUERY_STRING'])
        """
        try:
            form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
            #params = dict([part.split('=') for part in environ['QUERY_STRING'].split('&')])
            #msgId = int(params['id'])
        except:
            headers = [('Content-type', 'text/html')]
            start_response("200 OK", headers)
            return ["Error Processing provided ID"]

        id = int(form['id'].value)
        
        action = form['bttnSubmit'].value
        """
        
        id = int(self.get_value(form,post,'id',''))
        action = self.get_value(form,post,'bttnSubmit','')
        msg = meeplib.get_message(id)
        
        error = False
        errorMsg = ""
        response = "200 OK"
        
        headers = [('Content-type', 'text/html')]
        u = self.getUser(environ)
        if u == None:
            error = True
            errorMsg = """You must be logged in to proceed."""
        if msg == None:
            error = True
            errorMsg = """Message id: %d could not be found.""" % (id,)
        elif action == "Delete":
            if msg.author.username == u.username:
                meeplib.delete_message(msg)
                response = "302 Found"
                headers.append(('Location', '/'))
                errorMsg = "message removed"
            else:
                errorMsg = "You cannot delete another user's post."
        elif action == "Reply":
            title = ""
            message = form['replyText'].value
            user = meeplib.get_user(u.username)
            new_message = meeplib.Message(title, message, user, True)
            msg.add_reply(new_message)
            response = "302 Found"
            headers.append(('Location', '/'))
            errorMsg = "message replied"

        start_response(response, headers)
        return [errorMsg]

    def add_message(self, environ, start_response):
        err = (self.getUser(environ) is None)
        
        headers = [('Content-type', 'text/html')]
        start_response('200 OK', headers)
        return [render_page('addMessage.html', error=err)]

    def add_message_action(self, environ, start_response):
        u = self.getUser(environ)
        if u is None:
            headers = [('Content-type', 'text/html')]
            start_response("200 OK", headers)
            return ["You must be logged in to user this feature <p><a href='/login'>Log in</a><p><a href='/'>Show messages</a>"]


        post = (environ.get('REQUEST_METHOD') == 'POST')
        if post:
        	form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
        else:
            form = parse_qs(environ['QUERY_STRING'])

        title = self.get_value(form,post,'title','')
        message = self.get_value(form,post,'message','')
        
        new_message = meeplib.Message(title, message, u)

        headers = [('Content-type', 'text/html')]
        headers.append(('Location', '/'))
        start_response("302 Found", headers)
        return ["message added"]
        
    
    def delete_loggedin_user_action(self, environ, start_response):
        headers = [('Content-type', 'text/html')]
        u = self.getUser(environ)
        if u.username is None:
            start_response("200 OK", headers)
            return ["You must be logged in to delete your user. <p><a href='/login'>Log in</a><p><a href='/'>Show messages</a>"]
        
        meeplib.delete_user(u)
        self.log_user_out(environ, headers)
        
        headers = [('Content-type', 'text/html')]
        start_response("200 OK", headers)
        return ["You have successfully deleted this user."]
        
        
    def __call__(self, environ, start_response):
        # store url/function matches in call_dict
        call_dict = { '/': self.index,
                      '/login': self.login,
                      '/logout': self.logout,
                      '/create_user': self.create_user,
                      '/m/add': self.add_message,
                      '/m/add_action': self.add_message_action,
                      '/m/alterMessage': self.alter_message_action
                      }

        # see if the URL is in 'call_dict'; if it is, call that function.
        url = environ['PATH_INFO']
        if environ['PATH_INFO'] == '/favicon.ico':
            status = '404 Not Found'
            start_response(status, [('Content-type', 'text/html')])
            return []
        """
        print 'REQUEST_METHOD %s' % (environ['REQUEST_METHOD'],)
        print 'PATH_INFO %s' % (environ['PATH_INFO'],)
        print 'SCRIPT_NAME %s' % (environ['SCRIPT_NAME'],)
        print 'QUERY_STRING %s' % (environ['QUERY_STRING'],)
        print 'CONTENT_TYPE %s' % (environ['CONTENT_TYPE'],)
        print 'CONTENT_LENGTH %s' % (environ['CONTENT_LENGTH'],)
        print 'SERVER_NAME %s' % (environ['SERVER_NAME'],)
        print 'SERVER_PORT %s' % (environ['SERVER_PORT'],)
        print 'SERVER_PROTOCOL %s' % (environ['SERVER_PROTOCOL'],)
        """
        fn = call_dict.get(url)

        if fn is None:
            start_response("404 Not Found", [('Content-type', 'text/html')])
            return ["Page not found."]

        try:
            return fn(environ, start_response)
        except:
            tb = traceback.format_exc()
            print tb
            x = "<h1>Error!</h1><pre>%s</pre>" % (tb,)

            status = '500 Internal Server Error'
            start_response(status, [('Content-type', 'text/html')])
            return [x]
