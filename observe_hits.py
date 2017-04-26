from time import sleep
import configparser
import logging
from lib.cache import Cache


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("simulator")

config = configparser.ConfigParser()
config.read("config.ini")

CACHE_1 = Cache(config.get('Defaults', 'memcache_address_1'))
CACHE_2 = Cache(config.get('Defaults', 'memcache_address_2'))

while True:
    c1_total_hit_number = CACHE_1.get_total_hit()
    c2_total_hit_number = CACHE_2.get_total_hit()
    print(
        "CACHE 1 : {0} | CACHE 2 : {1} | Diff : {2}"
        .format(
            c1_total_hit_number,
            c2_total_hit_number,
            c1_total_hit_number-c2_total_hit_number
        )
    )
    print("----")
    sleep(0.3)
