import logging
import sqlite3

from socks5man.SOCKS5Server import SOCKS5Server

class DbManager(object):
    def __init__(self):
        self.db_name = "socks5man.sqlite"
        self.conn = None
        self.cursor = None

    def open_connection(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_name)

        if self.cursor is None:
            self.cursor = self.conn.cursor()

    def close_connection(self):
        if self.cursor is not None:
            self.cursor.close()
            self.cursor = None

        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def create_tables_if_not_existing(self):
        self.open_connection()

        with open("socks5man/server.sql", "r") as fp:
            self.cursor.execute(fp.read())
            self.conn.commit()

        self.close_connection()

    def add_server(self, server):
        success = False
        query = """
            INSERT INTO server
                (server_id, ip, port, username, password,
                country, last_checked, last_used, active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        args = (
            server.identifier, server.ip, server.port,
            server.username, server.password,
            server.country, server.last_checked,
            server.last_used, server.active,
        )

        try:
            self.cursor.execute(query, args)
            self.conn.commit()
            success = True
        except sqlite3.Error as e:
            logging.error("Failed to insert new server: %s", e)

        return success

    def update_server_stats(self, server):
        success = False
        query = """
            UPDATE server
            SET last_checked = ?, last_used = ?,
                active= ? WHERE server_id = ?
        """

        args = (
            server.last_checked, server.last_used,
            server.active, server.identifier,
        )

        try:
            self.cursor.execute(query, args)
            self.conn.commit()
            success = True
        except sqlite3.Error as e:
            logging.error("Failed to update server information: %s", e)

        return success

    def get_longest_unused_server(self):
        query = """
            SELECT * FROM server WHERE active = 1
            ORDER BY last_used ASC LIMIT 1
        """

        try:
            self.cursor.execute(query)
            server_info = self.cursor.fetchone()
        except sqlite3.Error as e:
            logging.error("Failed to get longest unused server: %s", e)

        if server_info is None:
            return None

        server = SOCKS5Server()
        server.identifier = server_info[0]
        server.ip = server_info[1]
        server.port = server_info[2]
        server.username = server_info[3]
        server.password = server_info[4]
        server.country = server_info[5]
        server.last_checked = server_info[6]
        server.last_used = server_info[7]
        server.active = server_info[8]
        return server
