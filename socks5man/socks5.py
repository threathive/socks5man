import logging
import socket
import socks
import time

from socks5man.constants import IP_API_URL
from socks5man.database import Database
from socks5man.helpers import (
    get_over_socks5, is_ipv4, get_ipv4_hostname, approximate_bandwidth
)

log = logging.getLogger(__name__)

db = Database()

class Socks5(object):
    """Socks5 wrapper class. Retrieve info and verify if socks
     is operational"""

    def __init__(self, db_socks5):
        self.db_socks5 = db_socks5

    def verify(self):
        """Test if this socks5 can be connected to and retrieve its own
        IP through the configured IP api. Automatically updates the
        'operational' value in the database"""
        operational = False
        ip = self.host
        if not is_ipv4(ip):
            ip = get_ipv4_hostname(ip)

        response = get_over_socks5(
            IP_API_URL, self.host, self.port, username=self.username,
            password=self.password, timeout=3
        )
        # TODO replace timeout with config timeout

        if response and response == ip:
            operational = True

        db.set_operational(self.id, operational)
        return operational

    def approx_bandwidth(self):
        """Calculate an approximate Mbit/s download speed using
        the file specified in the config to download. Automatically
        updated in the database"""
        approx_bandwidth = approximate_bandwidth(
            self.host, self.port, username=self.username,
            password=self.password, connecttime=self.connect_time, times=2
        )
        # TODO Get times from config
        db.set_approx_bandwidth(self.id, approx_bandwidth)
        return approx_bandwidth

    def measure_connection_time(self):
        """Measure the time it takes to connect to the specified connection
        test URL in the config. Result is automatically stored in the
         database"""
        s = socks.socksocket()
        s.set_proxy(
            socks.SOCKS5, self.host, self.port, username=self.username,
            password=self.password
        )
        # TODO replace timeout with config
        s.settimeout(3)
        start = time.time()
        # TODO replace connect test URL with curl from config
        try:
            s.connect(("speedtest.xs4all.net", 80))
            s.close()
        except (socks.ProxyError, socket.error) as e:
            log.error("Error connecting in connection time test: %s", e)
            connect_time = None
        else:
            connect_time = time.time() - start

        db.set_connect_time(self.id, connect_time)
        return connect_time

    def to_dict(self):
        return self.db_socks5.to_dict()

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
    def bandwidth(self):
        return self.db_socks5.bandwidth

    @property
    def connect_time(self):
        return self.db_socks5.connect_time

    @property
    def description(self):
        return self.db_socks5.description

    def __repr__(self):
        return "<Socks5(host=%s, port=%s, country=%s, authenticated=%s)>" % (
            self.host, self.port, self.country, (
                self.username is not None and self.password is not None
            )
        )
