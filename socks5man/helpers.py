import logging
import os
import socket
import socks
import struct
import time
import urllib2

from socks5man.constants import IANA_RESERVERD_IPV4_RANGES, SPEEDTEST_FILE_URL

from geoip2 import database as geodatabase
from geoip2.errors import GeoIP2Error

log = logging.getLogger(__name__)

def cwd(*args):
    return os.path.join("", *args)

class Dictionary(dict):
    """Custom dict support reading keys as attributes"""

    def __getattr__(self, key):
        return self.get(key, None)

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

def is_reserved_ipv4(ip):
    """Check if the IP belongs to reserved addr_block.
    @param ip: IP address to verify.
    @return: boolean representing whether the IP belongs to
    a private addr_block or not.
    """

    for addr_block in IANA_RESERVERD_IPV4_RANGES:
        try:
            ipaddr = struct.unpack(">I", socket.inet_aton(ip))[0]
            netaddr, bits = addr_block.split("/")
            network_low = struct.unpack(">I", socket.inet_aton(netaddr))[0]
            network_high = network_low | (1 << (32 - int(bits))) - 1

            if ipaddr <= network_high and ipaddr >= network_low:
                return True
        except:
            continue

    return False

def is_ipv4(ip):
    """Try to parse string as Ipv4. Return True if succes, False
    otherwise"""
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False

georeader = geodatabase.Reader(cwd("GeoLite2-City.mmdb"))
def ipv4info(ip):
    """Returns a dict containing the country, country_code, and city for
    a given IPv4 address"""
    result = {
        "country": "unknown",
        "country_code": "unknown",
        "city": "unknown"
    }

    if is_reserved_ipv4(ip):
        return result

    try:
        geodata = georeader.city(ip)
        if geodata.country.name:
            result["country"] = geodata.country.name
        if geodata.country.iso_code:
            result["country_code"] = geodata.country.iso_code
        if geodata.city.name:
            result["city"] = geodata.city.name
    except GeoIP2Error:
        return result

    return result

def get_ipv4_hostname(hostname):
    """Get IPv4 for specified hostname. Return None on fail"""
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        return None

def validify_host_port(host, port):
    """Returns a dict with ip and port if both are valid, otherwise
    returns None"""

    if not is_ipv4(host):
        host = get_ipv4_hostname(host)
        if not host:
            return None

    if not isinstance(port, int):
        return None

    if port < 1 or port > 65534:
        return None

    return Dictionary(
        ip=host,
        port=port
    )

def get_over_socks5(url, host, port, username=None, password=None, timeout=3):
    """Make a HTTP GET request over socks5 of the given URL"""
    socks.set_default_proxy(
        socks.SOCKS5, host, port,
        username=username, password=password
    )

    response = None
    try:
        socket.socket = socks.socksocket
        response = urllib2.urlopen(url, timeout=timeout).read()
    except (socket.error, urllib2.URLError, socks.ProxyError) as e:
        log.error("Error making HTTP GET over socsk5: %s", e)
    finally:
        socket.socket = socket._socketobject
    return response

def approximate_bandwidth(host, port, username=None, password=None,
                          connecttime=0, maxfail=1, times=2):
    """Tries to determine the average download speed in Mbit/s.
    Higher 'times' values will result in more accurate speeds, but will
    take a longer time.
    @param connecttime: The time it takes on average to connect to the
    specified socks5. This value is subtracted from the total time it takes
    to download a test file.
    @param maxfail: The maximum amount of times the socks5 is allowed to
    timeout before the measurement should stop
    @param times: The amount of times the test file should be downloaded.
    Optimal amount would be 3-4.
    """
    total = 0
    fails = 0
    test_url = SPEEDTEST_FILE_URL
    try:
        urllib2.urlopen(test_url, timeout=5)
    except (socket.error, urllib2.URLError) as e:
        log.error("Failed to download speed test file: %s", e)
        return 0.0

    for t in range(times):
        start = time.time()
        response = get_over_socks5(
            test_url, host, port, username=username, password=password,
            timeout=10
        )
        # TODO get timeouts from config
        if not response:
            if fails >= maxfail:
                return 0.0
            fails += 1

        took = time.time() - start

        # Take into account a connection time to get a more
        # accurate bandwidth
        if connecttime:
            took -= connecttime

        # Calculate the approximate Mbit/s
        speed = (len(response) / took) / 1000000 * 8

        # If the used file to measure is smaller than approx 1 MB,
        # add a small amount as the small size might cause the TCP window
        # to stay small
        if len(response) < 1000000:
            speed += speed * 0.1

        total += speed

    return total / times
