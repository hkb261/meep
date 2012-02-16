import meeplib
import traceback
import cgi
import meepcookie
from cgi import parse_qs, escape


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
        
    def index(self, environ, start_response):
        
        user = self.getUser(environ)
        if user != None:
            s = ["""you are logged in as user: %s.<p><a href='/m/add'>Add a message</a><p><a href='/logout'>Log out</a><p><a href='/m/list'>Show messages</a>""" % (user.username,)]
        else:
            s=["""Please login to create and delete messages<p><a href='/login'>Log in</a><p><a href='/create_user'>Create a New User</a><p><a href='/m/list'>Show messages</a>"""]
        
        start_response("200 OK", [('Content-type', 'text/html')])
        return s

    def login(self, environ, start_response):
        headers = [('Content-type', 'text/html')]

        print "number of users: %d" %(len(meeplib._users),)

        print "do i have input?", environ['wsgi.input']
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
        print "form", form

        try:
            username = form['username'].value
            # retrieve user
            print "we gots a username", username
        except KeyError:
            username = ''
            print "no user input"

        try:
            password = form['password'].value
            print "we gots a password", password
        except KeyError:
            password = ''
            print 'no password input'

        s=[]

        ##if we have username and password
        if username != '' and password != '':
            user = meeplib.get_user(username)
            if user is not None and user.password == password:
                self.log_user_in(environ, headers, user.username)

                ## send back a redirect to '/'
                k = 'Location'
                v = '/'
                headers.append((k, v))
            elif user is None:
                s.append('''Login Failed! <br>
                    The Username you provided does not exist<p>''')

            else:
                ## they messed up the password
                s.append('''Login Failed! <br>
                    The Username or Password you provided was incorrect<p>''')

        ##if we have username or password but not both
        elif username != '' or password != '':
            s.append('''Login Failed! <br>
                    The Username or Password you provided was incorrect<p>''')

        start_response('302 Found', headers)

        ##if we have a valid username and password this is not executed
        s.append('''
                    <form action='login' method='post'>
                        <label>username:</label> <input type='text' name='username' value='%s'> <br>
                        <label>password:</label> <input type='password' name='password'> <br>
                        <input type='submit' name='login button' value='Login'></form>

                        <p><a href='/create_user'>Or Create a New User</a>''' %(username))
        return [''.join(s)]

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

        try:
            if post:
                username = form['username'].value
            else:
                username = form.get('username','')[0]
            print "we gots a username", username
        except:
            username = ''
            print "no user input"

        try:
            if post:
                password = form['password'].value
            else:
                password = form.get('password', '')[0]
            print "we gots a password", password
        except:
            password = ''
            print 'no password input'

        try:
            if post:
                password2 = form['password_confirm'].value
            else:
                password2 = form.get('password_confirm', '')[0]
            print "we gots a password", password
        except:
            password2 = ''
            print 'no password confirmation'

        s=[]
        
        ##if we have username and password and confirmation password
        if username != '':
            user = meeplib.get_user(username)
            ## user already exists
            print 'afterlookup'
            print user
            
            if user is not None:
                print 'here'
                s.append('''Creation Failed! <br>
                    User already exists, please use a different Username<p>''')
            ## user doesn't exist but they messed up the passwords
            elif password == '':
                print 'here2'
                s.append('''Creation Failed! <br>
                    Please fill in the Password field<p>''')
            elif password != password2:
                print 'here3'
                s.append('''Creation Failed! <br>
                    The Password and Confirmation Password you provided did not match<p>''')
            else:
                print 'creating new user'
                u = meeplib.User(username, password)
                ## send back a redirect to '/'
                k = 'Location'
                v = '/'
                headers.append((k, v))
                self.log_user_in(environ, headers, u.username)
                print 'created'
                start_response('302 Found', headers)
                return []
        elif password != '' or password2 != '':
            print 'here4'
            s.append('''Creation Failed! <br>
            Please provide a Username<p>''')


        start_response('200 OK', headers)
        ##if we have a valid username and password this is not executed
        s.append('''
                    <form action='create_user' method='post'>
                        <label>username:</label> <input type='text' name='username' value='%s'> <br>
                        <label>password:</label> <input type='password' name='password' value='%s'> <br>
                        <label>confirm password:</label> <input type='password' name='password_confirm' value='%s'> <br>
                        <input type='submit' name='create user button' value='Create'></form>''' %(username, password, password2))
        return [''.join(s)]

    def list_messages(self, environ, start_response):
        messages = meeplib.get_all_messages()

        template = """
        <form action='alterMessage' method='POST'>
            <div class="messageCont">
                <div class="messageTitle">
                    <p>%s</p>
                    <input type='submit' id='bttnDelete' name='bttnSubmit' value='Delete' onclick="return confirm('Are you sure you want to delete this message?');" />
                </div>
                <div class="message">%s</div>
                <div class="messageReply">
                    By: %s
                </div>
                <div class="replies">
                    {replies}
                </div>
                <div class="messageReply %s">
                    &nbsp;<a href="#">Reply</a>
                </div>
                <div class="replyCont">
                    Reply: <textarea type='text' name='replyText' class="replyInput" rows="2" ></textarea>
                    <input type='submit' id='bttnReply' name='bttnSubmit' value='Reply' />
                </div>
            </div>
            <input type='hidden' name='id' value='%d' />
        </form>
        """
        
        replyTemp = """
<div class="reply">
    <p>%s</p>
    <div class="messageReply">
        By: %s
    </div>
</div>
"""  
        s = []
        u = self.getUser(environ)
        for m in messages:
             hide = ""
             if u is None:
                 hide = "hidden"
             msg = template % (m.title, m.post, m.author.username, hide, m.id)
             replies = m.get_replies()
             rs = []
             for r in replies:
                 print r.post
                 rs.append(replyTemp% (r.post, r.author.username))
             msg = msg.replace('{replies}',"".join(rs))
             s.append(msg)
        
        html = open('messageList.html', 'r').read().replace('{messageList}',"".join(s))
        headers = [('Content-type', 'text/html')]
        start_response("200 OK", headers)
        
        return [html]

    def alter_message_action(self, environ, start_response):
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
        print action
        print id
        
        msg = meeplib.get_message(id)
        
        error = False
        errorMsg = ""
        response = "200 OK"
        
        headers = [('Content-type', 'text/html')]
        u = self.getUser(environ)
        if u == None:
            eror = True
            errorMsg = """You must be logged in to proceed."""
        if msg == None:
            error = True
            errorMsg = """Message id%d could not be found.""" % (msgId,)
        elif action == "Delete":
            if msg.author.username == u.username:
                meeplib.delete_message(msg)
                response = "302 Found"
                headers.append(('Location', '/m/list'))
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
            headers.append(('Location', '/m/list'))
            errorMsg = "message replied"

        start_response(response, headers)
        return [errorMsg]

    def add_message(self, environ, start_response):
        u = self.getUser(environ)
        if u is None:
            headers = [('Content-type', 'text/html')]
            start_response("302 Found", headers)
            return ["You must be logged in to user this feature <p><a href='/login'>Log in</a><p><a href='/m/list'>Show messages</a>"]

        headers = [('Content-type', 'text/html')]

        start_response("200 OK", headers)

        return '''<form action='add_action' method='GET'>Title: <input type='text' name='title'><br>Message:<input type='text' name='message'><br><input type='submit'></form>'''

    def add_message_action(self, environ, start_response):
        u = self.getUser(environ)
        if u.username is None:
            headers = [('Content-type', 'text/html')]
            start_response("302 Found", headers)
            return ["You must be logged in to user this feature <p><a href='/login'>Log in</a><p><a href='/m/list'>Show messages</a>"]


        print environ['wsgi.input']
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

        title = form['title'].value
        message = form['message'].value

        new_message = meeplib.Message(title, message, u)

        headers = [('Content-type', 'text/html')]
        headers.append(('Location', '/m/list'))
        start_response("302 Found", headers)
        return ["message added"]
    
    def delete_loggedin_user_action(self, environ, start_response):
        u = self.getUser(environ)
        if u.username is None:
            headers = [('Content-type', 'text/html')]
            start_response("200 OK", headers)
            return ["You must be logged in to delete your user. <p><a href='/login'>Log in</a><p><a href='/m/list'>Show messages</a>"]
        
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
                      '/m/list': self.list_messages,
                      '/m/add': self.add_message,
                      '/m/add_action': self.add_message_action,
                      '/m/alterMessage': self.alter_message_action\
                      }

        # see if the URL is in 'call_dict'; if it is, call that function.
        url = environ['PATH_INFO']
        if environ['PATH_INFO'] == '/favicon.ico':
            status = '404 Not Found'
            start_response(status, [('Content-type', 'text/html')])
            return []
        print 'REQUEST_METHOD %s' % (environ['REQUEST_METHOD'],)
        print 'PATH_INFO %s' % (environ['PATH_INFO'],)
        print 'SCRIPT_NAME %s' % (environ['SCRIPT_NAME'],)
        print 'QUERY_STRING %s' % (environ['QUERY_STRING'],)
        print 'CONTENT_TYPE %s' % (environ['CONTENT_TYPE'],)
        print 'CONTENT_LENGTH %s' % (environ['CONTENT_LENGTH'],)
        print 'SERVER_NAME %s' % (environ['SERVER_NAME'],)
        print 'SERVER_PORT %s' % (environ['SERVER_PORT'],)
        print 'SERVER_PROTOCOL %s' % (environ['SERVER_PROTOCOL'],)
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
