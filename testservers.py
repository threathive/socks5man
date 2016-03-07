#!/usr/bin/env python

import logging

from socks5man.ServerManager import ServerManager

print("Testing the connection for all servers in the database")

ServerManager().test_all_servers()

print("All server statuses updated")