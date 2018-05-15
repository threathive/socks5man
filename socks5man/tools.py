import logging
import os
import shutil
import time
import urllib2

from socks5man.config import cfg
from socks5man.database import Database
from socks5man.socks5 import Socks5
from socks5man.misc import cwd, unpack_mmdb

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

def update_geodb():
    version_file = cwd("geodb", ".version")
    if not os.path.isfile(version_file):
        log.error("No geodb version file '%s' is missing", version_file)
        return

    with open(version_file, "rb") as fp:
        current_version = fp.read()

    try:
        latest_version = urllib2.urlopen(cfg("geodb", "geodb_md5_url")).read()
    except urllib2.URLError as e:
        log.error("Error retrieving latest geodb version hash: %s", e)
        return

    if current_version == latest_version:
        log.info("GeoIP database at latest version")
        return

    extracted = cwd("geodb", "extracted")
    renamed = None
    if os.path.exists(extracted):
        renamed = cwd("geodb", "old-extracted")
        os.rename(extracted, renamed)

    try:
        url = cfg("geodb", "geodb_url")
        log.info("Downloading latest version: '%s'", url)
        mmdbtar = urllib2.urlopen(url).read()
    except urllib2.URLError as e:
        log.error(
            "Failed to download new mmdb tar. Is the URL correct? %s", e
        )
        if renamed:
            log.error("Restoring old version..")
            os.rename(renamed, extracted)
        return

    tarpath = cwd("geodb", "geodblite.tar.gz")
    with open(tarpath, "wb") as fw:
        fw.write(mmdbtar)

    os.mkdir(extracted)

    unpack_mmdb(tarpath, cwd("geodb", "extracted", "geodblite.mmdb"))
    log.info("Version update complete")

    if renamed:
        log.debug("Removing old version")
        shutil.rmtree(renamed)
