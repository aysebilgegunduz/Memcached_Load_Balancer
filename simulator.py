import requests
import configparser
import logging
from lib.cache import Cache
from lib.user import UserThread

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("simulator")

config = configparser.ConfigParser()
config.read("config.ini")

CREATE_USER_URL = config.get("Defaults", "create_user_url")
HOMEPAGE_URL = config.get("Defaults", "homepage_url")

CACHE_1 = Cache(config.get('Defaults', 'memcache_address_1'))
CACHE_2 = Cache(config.get('Defaults', 'memcache_address_2'))

Q1_SLEEP_START = config.getint('Defaults', 'q1_sleep_start')
Q1_SLEEP_END = config.getint('Defaults', 'q1_sleep_end')
Q2_SLEEP_START = config.getint('Defaults', 'q2_sleep_start')
Q2_SLEEP_END = config.getint('Defaults', 'q2_sleep_end')

NUMBER_OF_THREAD = config.getint('Defaults', 'number_of_thread')
MAX_USER = config.getint("Defaults", "max_number_of_client")

#stored cookies in this list.
users = []

# Creating MAX_USER number of user
logger.info('-- Starting create of {0} user --'.format(MAX_USER))
for i in range(MAX_USER):
    logger.info("Creating user {0}".format(i+1))
    r = requests.get(CREATE_USER_URL)
    users.append(r.cookies)

# I have N number of user. It's time to behave like user:)
logger.info('-- Starting {0} number of user thread --'.format(NUMBER_OF_THREAD))
for user_cookie in users:
    for i in range(NUMBER_OF_THREAD):
        # queues have different number of sleep time between 2 request to the HOMEPAGE_URL
        logger.info(
            "-- Starting thread for user. Cookies : user_id={0}; cache_server_id={1}"
                .format(
                user_cookie.get('user_id'),
                user_cookie.get('cache_server_id')
            )
        )
        if user_cookie.get('cache_server_id') == "2":
            sleep_start = Q2_SLEEP_START
            sleep_end = Q2_SLEEP_END
        else:
            sleep_start = Q1_SLEEP_START
            sleep_end = Q1_SLEEP_END

        thread = UserThread(HOMEPAGE_URL, user_cookie)
        thread.set_timer(sleep_start, sleep_end)
        thread.start()
logger.info('-- All threads are started. Run observer_hits.py at another terminal --')


