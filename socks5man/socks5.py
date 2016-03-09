import logging
import socket
import socks
import time
import uuid
import urllib2

class TestSOCKS5(object):
    def __init__(self, ip, port, username="", password=""):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password

        self.test_url = "https://api.ipify.org/"

        self.test_passed = False

    def test(self, test_times=1):
        '''Sends HTTPS request to ipify API through the specified
        SOCKS5 server and matches if the response matches the SOCKS5 IP'''

        socks.setdefaultproxy(socks.SOCKS5, self.ip, self.port, rdns=True,
                              username=self.username, password=self.password)
        socket.socket = socks.socksocket

        times_connected = 0

        try:
            for n in range(0, test_times):
                answer = urllib2.urlopen(self.test_url, timeout=5).read()

                if answer == self.ip:
                    times_connected += 1

        except Exception as e:
            logging.error("Error SOCKS5 connection test: %s", e)

        # Restore socket
        socket.socket = socket._socketobject

        if times_connected == test_times:
            self.test_passed = True
            return True
        else:
            return False

class SOCKS5Server:
    def __init__(self, db_tuple=None):

        self.identifier = str(uuid.uuid4())
        self.active = False
        self.port = None
        self.ip = None
        self.password = None
        self.username = None
        self.last_used = 0
        self.last_checked = 0
        self.country = None

        # Strings used in web
        self.last_used_human = None
        self.last_checked_human = None
        self.active_human = None

        if db_tuple is not None:
            self._set_server_info(db_tuple)


    def _set_server_info(self, db_tuple):

        self.identifier = db_tuple[0]
        self.ip = db_tuple[1]
        self.port = db_tuple[2]
        self.username = db_tuple[3]
        self.password = db_tuple[4]
        self.country = db_tuple[5]
        self.last_checked = db_tuple[6]
        self.last_used = db_tuple[7]
        self.active = db_tuple[8]
        self.last_checked_human = self.get_human_last_checked_time()
        self.last_used_human = self.get_human_last_used_time()
        self._update_active_human()


    def retrieve_country(self):
        '''Use ipinfo.io to try and the country for the IP'''

        url = "http://ipinfo.io/%s/country" % self.ip
        try:
            # Ask ipinfo for the country code. Remove stuff we don't want
            self.country = urllib2.urlopen(url).read().rstrip()
        except urllib2.HTTPError as e:
            logging.error("Error while asking ipinfo.io for country for ip: %s",
                          e)


    def is_ip_valid(self):
        '''Checks if the currently set IP is valid'''

        if self.ip is None:
            return False
        try:
            socket.inet_aton(self.ip)
            return True
        except socket.error:
            return False

    def is_port_valid(self):
        '''Checks is the currently set port is valid'''

        if self.port is None:
            return False
        if not isinstance(self.port, (int, long)):
            return False
        if self.port > 0 and self.port < 65535:
            return True

    def is_authenticated(self):
        '''Returns true if a username/password is needed for this server'''

        empty = [None, ""]

        if self.password not in empty or self.username not in empty:
            return True
        return False

    def is_active(self):
        '''Tests if this SOCKS5 server is still operating'''

        if not self.is_authenticated():
            self.username = None
            self.password = None

        test_connection = TestSOCKS5(self.ip, self.port,
                                     self.username, self.password)

        self._update_last_checked_time()
        if test_connection.test():
            self.active = True
            return True
        self.active = False
        return False

    def _update_active_human(self):
        '''Updates the active_human field to Offline or Online'''
        if self.active == 1:
            self.active_human = "Online"
        else:
            self.active_human = "Offline"

    def _update_last_checked_time(self):
        '''Updates the last checked time to current time in seconds'''

        self.last_checked = time.mktime(time.gmtime())

    def update_last_used_time(self):
        '''Updates the last used time to current time in seconds'''

        self.last_used = time.mktime(time.gmtime())

    def get_human_last_used_time(self):
        '''Returns a human readable string of the last date/time used'''

        return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(self.last_used))

    def get_human_last_checked_time(self):
        '''Returns a human readable string of the last date/time checked'''

        return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(self.last_checked))

    def get_json_settings(self):
        return {
            "id": self.identifier,
            "active": self.active_human,
            "ip": self.ip,
            "port": self.port,
            "authenticated": self.is_authenticated(),
            "username": self.username,
            "password": self.password,
            "last_used": self.last_used_human,
            "last_checked": self.last_checked_human,
            "country": self.country,
        }
