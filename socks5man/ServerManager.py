import logging

from socks5man.db import DbManager
from socks5man.socks5 import SOCKS5Server

class ServerManager(object):
    def __init__(self):
        self.dbm = DbManager()

    def get_server_json(self):
        '''Get server info in JSON for for the
        longest unused server'''

        json_response = None
        server = self.dbm.get_longest_unused_server()

        if server is None:
            return json_response

        json_response = server.get_json_settings()

        server.update_last_used_time()

        self.dbm.update_server_stats(server)

        return json_response

    def add_server(self, request):
        '''Validates the information in the request
        ,stores the server and returns a string status response'''

        server = SOCKS5Server()
        server.ip = request.form.get("ip")

        server.username = request.form.get("username")
        server.password = request.form.get("password")
        server.country = request.form.get("country")

        try:
            server.port = int(request.form.get("port"))
        except ValueError:
            return "Invalid port"

        if not server.is_ip_valid():
            return "Invalid IPv4 address"
        if not server.is_port_valid():
            return "Invalid port"

        if self.dbm.add_server(server):
            return "Server added! =)"
        else:
            return "Error while adding server to database"


    def test_all_servers(self):
        '''Tests all SOCKS5 servers in the db and updates
        the status information'''

        servers = self.dbm.get_all_servers()
        if servers is None:
            logging.warn("No servers to test!")
            return

        for info in servers:
            server = SOCKS5Server(info)
            server.is_active()
            self.dbm.update_server_stats(server)


