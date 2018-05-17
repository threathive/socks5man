from socks5man.misc import set_cwd, create_cwd
from socks5man.helpers import (
    Dictionary, is_ipv4, is_reserved_ipv4, GeoInfo, get_ipv4_hostname,
    validify_host_port, get_over_socks5, approximate_bandwidth
)

from tests.helpers import CleanedTempFile

def test_dictionary():
    d = {
        "hello": 10,
        "stuff": False,
        "tosti": "Yes"
    }
    d2 = Dictionary(d)
    assert d2.hello == 10
    assert not d2.stuff
    assert d2.tosti == "Yes"

def test_is_reserve_ipv4():
    reserved = [
        "127.0.0.1", "192.168.0.29", "172.16.18.10", "169.254.13.3",
        "10.0.10.11", "0.0.0.9", "255.255.255.0", "192.88.99.17"
    ]
    for ip in reserved:
        assert is_reserved_ipv4(ip)

    public = [
        "8.8.8.8", "45.19.77.17", "8.8.4.4", "123.38.177.1", "192.167.1.1",
        "11.0.0.1", "1.0.0.0"
    ]
    for ip in public:
        assert not is_reserved_ipv4(ip)

def test_is_ipv4():
    ipv4 = [
        "8.8.8.8", "45.19.77.17", "8.8.4.4", "123.38.177.1", "192.167.1.1",
        "11.0.0.1", "1.0.0.0", "127.0.0.1", "192.168.0.29", "172.16.18.10",
        "169.254.13.3", "10.0.10.11", "0.0.0.9", "255.255.255.0",
        "192.88.99.17"
    ]

    for ip in ipv4:
        assert is_ipv4(ip)

    hostnames = ["example.com", "hostname.example.com"]
    for h in hostnames:
        assert not is_ipv4(h)

    ipv6 = ["2001:db8:85a3:8d3:1319:8a2e:370", "0:0:0:0:0:0:0:1"]

    for ipv6 in ipv6:
        assert not is_ipv4(ipv6)

class TestGeoInfo(object):

    def setup_class(self):
        self.tempfile = CleanedTempFile()

    def teardown_class(self):
        self.tempfile.clean()

    def test_ipv4info(self):
        tmppath = self.tempfile.mkdtemp()
        set_cwd(tmppath)
        create_cwd(tmppath)

        geo = GeoInfo()
        res = geo.ipv4info("93.184.216.34")
        assert res["country"] == "United States"
        assert res["country_code"] == "US"
        assert res["city"] == "Norwell"

def test_get_ipv4_hostname():
    ip = get_ipv4_hostname("example.com")
    assert ip == "93.184.216.34"

def test_get_ipv4_hostname_invalid():
    ip = get_ipv4_hostname("nonexisting.stuff.tosti")
    assert ip is None
