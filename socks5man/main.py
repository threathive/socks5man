import click
import csv
import logging
import os
import sys

from socks5man.database import Database
from socks5man.exceptions import Socks5manError
from socks5man.logs import init_loggers
from socks5man.manager import Manager
from socks5man.tools import verify_all, update_geodb

log = logging.getLogger(__name__)
db = Database()
m = Manager()

@click.group()
@click.option("-d", "--debug", is_flag=True, help="Enable debug logging")
def main(debug):
    level = logging.INFO
    if debug:
        level = logging.DEBUG
    init_loggers(level)

@main.command()
@click.option("-s", "--service", is_flag=True, help="Start a service that keeps verifying all servers at the interval specified in the config")
def verify(service):
    """Verify if the servers are operational"""
    try:
        verify_all(service)
    except KeyboardInterrupt:
        log.warning("CTRL+C detected! exiting.")
        sys.exit(0)

@main.command()
@click.argument("host")
@click.argument("port", type=click.INT)
@click.option("-u", "--username", help="Username for this socks5 server")
@click.option("-p", "--password", help="Password for this socks5 server")
@click.option("-d", "--description", help="Description for this socks5 server")
def add(host, port, username, password, description):
    """Add socks5 server"""
    if username and not password or password and not username:
        log.warning(
            "Both a username and password need to be provided if the socks5"
            " server is authenticated"
        )
        sys.exit(1)

    try:
        entry = m.add(
            host, port, username=username, password=password,
            description=description
        )
    except Socks5manError as e:
        log.error("Failed to add socks5 server: %s", e)
        sys.exit(1)

    log.info(
        "Added socks5 '%s:%s', country=%s, country code=%s, city=%s",
        entry.host, entry.port, entry.country, entry.country_code, entry.city
    )

@main.command()
@click.argument("file_path")
@click.option("-d", "--description", help="Description for this socks5 server bulk")
def bulk_add(file_path, description):
    """Bulk add socks5 servers from CSV file"""
    if not os.path.isfile(file_path):
        log.error("File '%s' does not exist", file_path)
        sys.exit(1)

    if not os.access(file_path, os.R_OK):
        log.error("No read access on file '%s'", file_path)
        sys.exit(1)

    with open(file_path, "rb") as fp:
        try:
            socks5s = [socks5 for socks5 in csv.DictReader(fp)]
        except csv.Error as e:
            log.error("Error reading CSV file: %s", e)
            sys.exit(1)

    if not socks5s:
        log.warning("No socks5 servers to add")
        sys.exit(1)

    try:
        count = m.bulk_add(socks5s, description=description)
        if count:
            log.info("Successfully bulk added %s servers", count)
        else:
            log.error(
                "Failed to bulk add servers. See log for more information"
            )
    except Socks5manError as e:
        log.error("Failed to bulk add: %s", e)
        sys.exit(1)

@main.command()
def update_geoinfo():
    """Update version of the used Maxmind geodb"""
    update_geodb()
