from socks5man.DbManager import DbManager

class ServerManager(object):
    def __init__(self):
        self.dbm = DbManager()

    def get_server_json(self):
        json_response = None
        self.dbm.open_connection()
        server = self.dbm.get_longest_unused_server()

        if server is None:
            return json_response

        json_response = server.get_json_settings()

        server.update_last_used_time()

        self.dbm.update_server_stats(server)
        self.dbm.close_connection()

        return json_response
