from Cookie import SimpleCookie
from datetime import date, timedelta
    
def make_set_cookie_header(name, value, path='/'):
    """
    Makes a 'Set-Cookie' header.
    
    """
    c = SimpleCookie()
    c[name] = value
    c[name]['path'] = path
    
    # can also set expires and other stuff.  See
    # Examples under http://docs.python.org/library/cookie.html.

    s = c.output()
    (key, value) = s.split(': ')
    return (key, value)


def get_cookie_value(environ, name):
    c = SimpleCookie()
    c.load(environ.get('HTTP_COOKIE', ''))
    try:
        return c[name].value
    except:
        return ""
        
def delete_cookie(environ, name):
    c = SimpleCookie()
    c[name] = ''
    c[name]['expires'] = \
        d=date.today()-timedelta(days=30)

    s = c.output()
    (key, value) = s.split(': ')
    return (key, value)