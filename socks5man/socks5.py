import logging
import socket
import socks
import sys
import time

from socks5man.config import cfg
from socks5man.database import Database
from socks5man.helpers import (
    get_over_socks5, is_ipv4, get_ipv4_hostname, approximate_bandwidth,
    is_reserved_ipv4
)

log = logging.getLogger(__name__)

# Required for socks connecting to work on Windows
if sys.platform == "win32":
    import win_inet_pton

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
            cfg("operationality", "ip_api"), self.host, self.port,
            username=self.username, password=self.password,
            timeout=cfg("operationality", "timeout")
        )

        if response:
            if ip == response:
                operational = True

            # If a private ip is used, the api response will not match with
            # the configured host or its ip. There was however a response,
            # therefore we still mark it as operational
            elif is_reserved_ipv4(ip) and is_ipv4(response):
                operational = True

        db.set_operational(self.id, operational)
        return operational

    def approx_bandwidth(self):
        """Calculate an approximate Mbit/s download speed using
        the file specified in the config to download. Automatically
        updated in the database"""
        approx_bandwidth = approximate_bandwidth(
            self.host, self.port, username=self.username,
            password=self.password, times=cfg("bandwidth", "times"),
            timeout=cfg("bandwidth", "timeout")
        )
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

        s.settimeout(cfg("connection_time", "timeout"))
        start = time.time()
        try:
            s.connect((
                    cfg("connection_time", "hostname"),
                    cfg("connection_time", "port")
            ))
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
        if self.db_socks5.host:
            return self.db_socks5.host.encode("utf-8")
        return None

    @property
    def port(self):
        return self.db_socks5.port

    @property
    def country(self):
        if self.db_socks5.country:
            return self.db_socks5.country.encode("utf-8")
        return None

    @property
    def country_code(self):
        return self.db_socks5.country_code

    @property
    def city(self):
        if self.db_socks5.city:
            return self.db_socks5.city.encode("utf-8")
        return None

    @property
    def username(self):
        if self.db_socks5.username:
            return self.db_socks5.username.encode("utf-8")
        return None

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
        if self.db_socks5.description:
            return self.db_socks5.description.encode("utf-8")
        return None

    def __repr__(self):
        return "<Socks5(host=%s, port=%s, country=%s, authenticated=%s)>" % (
            self.host, self.port, self.country, (
                self.username is not None and self.password is not None
            )
        )
