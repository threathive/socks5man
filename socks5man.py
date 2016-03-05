#!/usr/bin/env python

import json

from socks5man import Api
from socks5man.DbManager import DbManager
from socks5man.Logger import Logger

Logger().setup_logger()
DbManager().create_tables_if_not_existing()

Api.start_api()