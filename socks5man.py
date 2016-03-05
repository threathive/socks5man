#!/usr/bin/env python

import socks5man.api

from socks5man.db import DbManager
from socks5man.logger import Logger

Logger().setup_logger()
DbManager().create_tables_if_not_existing()

socks5man.api.start_api()
