import logging

from socks5man.database import Database
from socks5man.exceptions import Socks5CreationError
from socks5man.helpers import (
    Dictionary, validify_host_port, ipv4info
)
from socks5man.socks5 import Socks5

log = logging.getLogger(__name__)

db = Database()

class Manager(object):

    def acquire(self, country=None, country_code=None, city=None,
                min_mbps_down=None, max_connect_time=None, update_usage=True,
                limit=1):

        socks5_result = db.find_socks5(
            country=country, country_code=country_code, city=city,
            min_mbps_down=min_mbps_down, max_connect_time=max_connect_time,
            update_usage=update_usage, limit=limit
        )

        return [Socks5(db_socks5) for db_socks5 in socks5_result]

    def add(self, host, port, username=None, password=None, description=None):
        if (not username and password) or (not password and username):
            raise Socks5CreationError(
                "Either no password and no password or both a password and a"
                "username should be provided on socks5 creation. It is not "
                "possible to provide only a username or password"
            )
        valid_entry = validify_host_port(host, port)

        if not valid_entry:
            raise Socks5CreationError(
                "Invalid host or port used. Invalid IP, non-existing hostname "
                ", or an invalid port specified. Host: %s, port: %s" % (
                    host, port
                )
            )

        entry = Dictionary(
            host=host,
            port=port,
            username=username,
            password=password
        )
        entry.update(ipv4info(valid_entry.ip))
        db.add_socks5(
            entry.host, entry.port, entry.country, entry.country_code,
            city=entry.city, username=entry.username, password=entry.password,
            description=description
        )

    def bulk_add(self, socks5_dict_list, description=None):
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
                continue

            if description:
                entry["description"] = description

            new_entry = {
                "host": None,
                "port": None,
                "country": None,
                "country_code": None,
                "city": None,
                "username": None,
                "password": None,
                "operational": False,
                "description": None
            }
            new_entry.update(entry)
            new_entry.update(ipv4info(valid_entry.ip))
            new.append(new_entry)

        db.bulk_add_socks5(new)
