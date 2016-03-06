#!/usr/bin/env python

import logging

from socks5man.ServerManager import ServerManager

log = logging.getLogger(__name__)
log.info("Testing the connection for all servers in the database")

ServerManager().test_all_servers()

log.info("All server statuses updated")