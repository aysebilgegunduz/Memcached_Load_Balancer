from flask import Flask
from flask import make_response
from flask import request
from lib.cache import Cache
import names
import configparser

config = configparser.ConfigParser()
config.read("config.ini")

MAX_USER = config.getint('Defaults', 'max_number_of_client')
CACHE_1 = Cache(config.get('Defaults', 'memcache_address_1'))
CACHE_2 = Cache(config.get('Defaults', 'memcache_address_2'))

CURRENT_USER_NUMBER = 0

app = Flask(__name__)


@app.route('/create_user')
def create_user():
    """
    The main method for creating a new user.
    I don't create a new user actually. just randomly generate first name
    :return:
    """
    global MAX_USER, CURRENT_USER_NUMBER

    if CURRENT_USER_NUMBER == MAX_USER:  # Checking number of user created.
        return "Maximum number of user reached. Not creating a new user"

    CURRENT_USER_NUMBER += 1  # Increase user number.

    """
    This is important. At the initial phase, I am creating N number of user.
    Those users will be written to the cache server equally. That means;
    Cache 1 and 2 will have N/2 number of user at initial phase
    I am using odd/even approach for this reason.
    """
    if CURRENT_USER_NUMBER % 2 == 0:
        # Write this user to the cache 1.
        CACHE_1.create_user(
            CURRENT_USER_NUMBER,
            names.get_first_name()
        )
        cache_server_id = 1
    else:
        # Write this user to the cache 2.
        CACHE_2.create_user(
            CURRENT_USER_NUMBER,
            names.get_first_name()
        )
        cache_server_id = 2

    resp = make_response("Your user id = {0}".format(CURRENT_USER_NUMBER))
    resp.set_cookie("user_id", str(CURRENT_USER_NUMBER))
    resp.set_cookie("cache_server_id", str(cache_server_id))

    return resp


@app.route('/homepage')
def home_page():
    user_id = request.cookies.get('user_id')
    cache_server_id = request.cookies.get('cache_server_id')
    if cache_server_id == "1":
        name = CACHE_1.get_user(user_id)
        if name is None:
            if CACHE_2.get_user(user_id):
                resp = make_response("Hello {0}. Welcome back <3".format(name))
                resp.set_cookie("user_id", str(user_id))
                resp.set_cookie("cache_server_id", str(2))
                return resp
    elif cache_server_id == "2":
        name = CACHE_2.get_user(user_id)
        if name is None:
            if CACHE_1.get_user(user_id):
                resp = make_response("Hello {0}. Welcome back <3".format(name))
                resp.set_cookie("user_id", str(user_id))
                resp.set_cookie("cache_server_id", str(1))
                return resp
    else:
        return "cache_server_id can be only 1 or 2."

    resp = make_response("Hello {0}. Welcome back <3".format(name))
    return resp
