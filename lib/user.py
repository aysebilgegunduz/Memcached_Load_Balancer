import threading
import requests
from random import randint
from time import sleep


class UserThread(threading.Thread):
    """
    C1 have to much more load than C2. Thus we are using sleep() function
    at the end of run(). We also us randint() in order to make it looks like real user.
    """
    sleep_start = None
    sleep_end = None

    def __init__(self, url, cookie):
        threading.Thread.__init__(self)
        self.url = url
        self.cookie = cookie

    def set_timer(self, sleep_start, sleep_end):
        self.sleep_start = sleep_start
        self.sleep_end = sleep_end

    def run(self):
        while True:
            r = requests.get(self.url, cookies=self.cookie)
            """
            Important..! I am re-setting cookies because server
            side. Maybe web app moved my data to another cache server.
            That means cache_server_id -COOKIE value- changed..!
            """
            if r.cookies:
                self.cookie = r.cookies

            sleep(randint(self.sleep_start, self.sleep_end))