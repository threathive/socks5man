from socks5man.database import Database
from socks5man.helpers import get_over_socks5, is_ipv4, get_ipv4_hostname
from socks5man.constants import IP_API_URL
import urllib2
import socket
import socks

db = Database()

class Socks5(object):
    """Socks5 wrapper class. Retrieve info and verify if socks
     is operational"""

    def __init__(self, db_socks5):
        self.db_socks5 = db_socks5

    def verify(self):
        response = get_over_socks5(
            IP_API_URL, self.host, self.port, username=self.username,
            password=self.password
        )
        if not response:
            return False
        ip = self.host
        if not is_ipv4(self.host):
            ip = get_ipv4_hostname(self.host)
        if ip == response:
            return True
        return False

    def approx_bandwidth(self):
        pass

    @property
    def id(self):
        return self.db_socks5.id

    @property
    def host(self):
        return self.db_socks5.host

    @property
    def port(self):
        return self.db_socks5.port

    @property
    def country(self):
        return self.db_socks5.country

    @property
    def country_code(self):
        return self.db_socks5.country_code

    @property
    def city(self):
        return self.db_socks5.city

    @property
    def username(self):
        return self.db_socks5.username

    @property
    def password(self):
        return self.db_socks5.password

    @property
    def added_on(self):
        return self.db_socks5.added_on

    @property
    def last_use(self):
        return self.db_socks5.last_use

    @property
    def last_check(self):
        return self.db_socks5.last_check

    @property
    def operational(self):
        return self.db_socks5.operational

    @property
    def description(self):
        return self.db_socks5.description

    def __repr__(self):
        return "<Socks5(host=%s, port=%s, country=%s, authenticated=%s)>" % (
            self.host, self.port, self.country, (
                self.username is not None and self.password is not None
            )
        )
