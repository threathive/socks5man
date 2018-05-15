import logging
import time

from socks5man.config import cfg
from socks5man.database import Database
from socks5man.socks5 import Socks5

log = logging.getLogger(__name__)
db = Database()

def verify_all(service=False):

    last_bandwidth = None
    bandwidth_checked = False
    while True:
        for socks5 in db.list_socks5():
            socks5 = Socks5(socks5)

            log.info(
                "Testing socks5 server: '%s:%s'", socks5.host, socks5.port
            )
            if socks5.verify():
                log.debug("Operationality check: OK")
            else:
                log.warning(
                    "Operationality check (%s:%s): FAILED",
                    socks5.host, socks5.port
                )
                continue

            if cfg("connection_time", "enabled"):
                con_time = socks5.measure_connection_time()
                if con_time:
                    log.debug("Measured connection time: %s", con_time)
                else:
                    log.warning(
                        "Connection time measurement failed for: '%s:%s'",
                        socks5.host, socks5.port
                    )

            if cfg("bandwidth", "enabled"):
                if last_bandwidth:
                    waited = time.time() - last_bandwidth
                    if waited < cfg("socks5man", "bandwidth_interval"):
                        continue

                bandwidth_checked = True
                bandwidth = socks5.approx_bandwidth()
                if bandwidth:
                    log.debug(
                        "Approximate bandwidth: %s Mbit/s down", bandwidth
                    )
                else:
                    log.warning(
                        "Bandwidth approximation test failed for: '%s:%s'",
                        socks5.host, socks5.port
                    )

        if bandwidth_checked:
            bandwidth_checked = False
            last_bandwidth = time.time()

        if not service:
            break

        time.sleep(cfg("socks5man", "verify_interval"))
