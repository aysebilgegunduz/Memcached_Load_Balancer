from lib.cache import Cache
import configparser
from time import sleep

config = configparser.ConfigParser()
config.read("config.ini")

# Reading maximum number of client from configuration file.
MAX_USER = config.getint('Defaults', 'max_number_of_client')
DIFF_THRESHOLD = config.getint('Defaults', 'diff_threshold')

# Reading cache server IP addresses and then configuring the cache classes.
CACHE_1 = Cache(config.get('Defaults', 'memcache_address_1'))
CACHE_2 = Cache(config.get('Defaults', 'memcache_address_2'))

CURRENT_USER_NUMBER = 0


def cache_balancer():
    global DIFF_THRESHOLD, MAX_USER
    # Get total hit number from both queue.
    c1_number = CACHE_1.get_total_hit()
    c2_number = CACHE_2.get_total_hit()

    diff = c1_number - c2_number

    target_load = int(diff / 2)

    if abs(diff) <= DIFF_THRESHOLD:
        # C1 is more loaded but not enough. Even 40  -diff_threshold- not enough :-)
        print("Nothing to balance. Sleeping 3 seconds for next execution. zzzZ")
        return None

    if diff > DIFF_THRESHOLD:
        # cache-1 is too loaded. Find a proper user and move it to cache-2
        diff_list = []

        # Iterating on all user by fetching their hit number
        for i in range(1, MAX_USER+1):
            hit_value = CACHE_1.get_user_hit(i)
            if hit_value and hit_value > 0:
                name = CACHE_1.get_user(i, trigger_inc=False)
                if not isinstance(name, str):  # If returned data is not string, move next iteration.
                    continue
                diff_list.append(
                    {
                        'user_id': i,
                        'name': name,  # Going to use it while moving data.
                        'hit': hit_value,  # Going to use it while moving data to cache-2
                        'diff': abs(target_load-hit_value)  # That is important. selected smallest value later.
                     }
                )
        if diff_list:
            smallest_value = min(diff_list, key=lambda x: x['diff'])
            # Moving user to CACHE-2.
            CACHE_2.create_user(
                smallest_value.get('user_id'),
                smallest_value.get('name'),
                smallest_value.get('hit'),
            )
            # Remove old one from CACHE-1.
            CACHE_1.destroy(smallest_value.get('user_id'))
            CACHE_1.decrease_total_hit(smallest_value.get('hit'))
            print("C1 used more loaded. Balance is trigged...!")
            del diff_list, smallest_value, target_load  # Deleting temp variables just in case^^
            return 2

    elif diff < DIFF_THRESHOLD:
        # cache-2 is too loaded. Find a proper user and move it to cache-1
        diff_list = []

        # Iterating on all user by fetching their hit number
        for i in range(1, MAX_USER + 1):
            hit_value = CACHE_2.get_user_hit(i)
            if hit_value and hit_value > 0:
                diff_list.append(
                    {
                        'user_id': i,
                        'name': CACHE_2.get_user(i, trigger_inc=False),  # Going to use it while moving data.
                        'hit': hit_value,  # Going to use it while moving data
                        'diff': abs(target_load - hit_value)  # That is important. selected smallest value later.
                     }
                )
        if diff_list:
            smallest_value = min(diff_list, key=lambda x: x['diff'])
            # Creating same user on CACHE-2.
            CACHE_1.create_user(
                smallest_value.get('user_id'),
                smallest_value.get('name'),
                smallest_value.get('hit'),
            )
            # Remove old one from CACHE-1.
            CACHE_2.destroy(smallest_value.get('user_id'))
            CACHE_2.decrease_total_hit(smallest_value.get('hit'))
            print("C2 used more loaded. Balance is trigged...!")
            del diff_list, smallest_value, target_load  # Deleting temp variables just in case^
            return 1
    # No need to balance anything.
    return None

while True:
    cache_balancer()
    sleep(3)