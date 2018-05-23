import logging

from socks5man.database import Database
from socks5man.exceptions import Socks5CreationError
from socks5man.helpers import (
    Dictionary, GeoInfo, validify_host_port
)
from socks5man.socks5 import Socks5

log = logging.getLogger(__name__)

db = Database()

class Manager(object):

    def acquire(self, country=None, country_code=None, city=None,
                min_mbps_down=None, max_connect_time=None, update_usage=True):
        """Acquire a socks5 server that was tested to be operational. The
        returned socks5 server will automatically be marked as used.
        Acquiring is in a round-robin fashion.

        @param country: Country the socks5 server should be in
        @param country_code: 2-letter country code
        @param city: City the socks5 server should be in
        @param min_mbps_down: The minimum average download speed in
        mbits (float)
        @param max_connect_time: The maximum average connection time in seconds
        a socks5 server should have (float)
        """
        db_socks5 = db.find_socks5(
            country=country, country_code=country_code, city=city,
            min_mbps_down=min_mbps_down, max_connect_time=max_connect_time,
            update_usage=update_usage
        )
        if db_socks5:
            return Socks5(db_socks5[0])
        else:
            return None

    def add(self, host, port, username=None, password=None, description=None):
        """Add a socks5 server

        @param host: IP or hostname of the socks5 server
        @param port: Port of the socks5 server
        @param username: Username of the socks5 server (optional)
        @param password: Password for the socks5 server user (optional)
        @param description: Description to store with the socks5
        server (optional)
        """
        if (not username and password) or (not password and username):
            raise Socks5CreationError(
                "Either no password and no password or both a password and a"
                "username should be provided on socks5 creation. It is not "
                "possible to provide only a username or password"
            )

        valid_entry = validify_host_port(host, port)
        if not valid_entry:
            raise Socks5CreationError(
                "Invalid host or port used. Invalid IP, non-existing hostname"
                ", or an invalid port specified. Host: %s, port: %s" % (
                    host, port
                )
            )

        existing = db.view_socks5(host=host, port=port)
        if existing:
            raise Socks5CreationError(
                "Socks5 host and port combination: '%s:%s' already exists."
                " Socks5 ID is: %s" % (
                    host, port, existing.id
                )
            )

        entry = Dictionary(
            host=host,
            port=port,
            username=username,
            password=password
        )
        entry.update(GeoInfo.ipv4info(valid_entry.ip))
        socksid = db.add_socks5(
            entry.host, entry.port, entry.country, entry.country_code,
            city=entry.city, username=entry.username, password=entry.password,
            description=description
        )

        entry["id"] = socksid
        return entry

    def bulk_add(self, socks5_dict_list, description=None):
        """Bulk add multiple socks5 server. No duplicate checking is done.

        @param socks5_dict_list: A list of dictionaries that at a minimum
        contain the keys and valid values for 'host' and 'port'.
        """
        new = []
        for entry in socks5_dict_list:
            if "host" not in entry or "port" not in entry:
                continue

            password = entry.get("password")
            username = entry.get("username")
            if (not username and password) or (not password and username):
                log.warning(
                    "Either no password and no password or both a password "
                    "and a username should be provided on socks5 creation. It "
                    "is not possible to provide only a username or password"
                )
                continue

            valid_entry = validify_host_port(entry["host"], entry["port"])

            if not valid_entry:
                log.error("Invalid host or port provided")
                continue

            if description:
                entry["description"] = description

            new_entry = {
                "host": entry["host"],
                "port": valid_entry.port,
                "country": None,
                "country_code": None,
                "city": None,
                "username": username,
                "password": password,
                "operational": False,
                "description": entry.get("description")
            }
            new_entry.update(GeoInfo.ipv4info(valid_entry.ip))
            new.append(new_entry)

        if not new:
            raise Socks5CreationError("No socks5 servers to add provided")

        db.bulk_add_socks5(new)
        return len(new)

    def delete(self, socks5_id):
        """Delete socks5 with given id"""
        db.remove_socks5(socks5_id)

    def delete_all(self):
        """Remove all socks5 servers from the database"""
        db.delete_all_socks5()

    def list_socks5(self, country=None, country_code=None, city=None,
                    host=None, operational=None):
        """Retrieve list of socks5 servers using the specified filters"""
        socks5s = db.list_socks5(
            country=country, country_code=country_code, city=city,
            host=host, operational=operational
        )
        return [Socks5(s) for s in socks5s]
