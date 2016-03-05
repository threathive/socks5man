import logging
import socket
import socks
import urllib2

class TestSOCKS5:
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
            for n in range(0, self.min_success_connections):
                answer = urllib2.urlopen(self.test_url).read()

                if answer == self.ip:
                    times_connected += 1

        except Exception as e:
            logging.error("Error: %s", e)
            return False

        if times_connected == test_times:
            self.test_passed = True
            return True
        else:
            return False
