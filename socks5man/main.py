import click
import csv
import logging
import os
import sys

from socks5man.exceptions import Socks5manError
from socks5man.logs import init_loggers
from socks5man.manager import Manager
from socks5man.tools import verify_all, update_geodb

log = logging.getLogger(__name__)
m = Manager()

@click.group()
@click.option("-d", "--debug", is_flag=True, help="Enable debug logging")
def main(debug):
    level = logging.INFO
    if debug:
        level = logging.DEBUG
    init_loggers(level)

@main.command()
@click.option("-r", "--repeated", is_flag=True, help="Continuously keep verifying all servers at the interval specified in the config")
def verify(repeated):
    """Verify if the servers are operational."""
    try:
        verify_all(repeated)
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
    """Add socks5 server."""
    if username and not password or password and not username:
        log.warning(
            "Both a username and password need to be provided if the socks5"
            " server is authenticated"
        )
        sys.exit(1)

    try:
        entry = m.add(
            host, port, username=username, password=password,
            description=unicode(description)
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
    """Bulk add socks5 servers from CSV file. It does not verify if any of the provided
    servers already exist."""
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

@main.command("update-geodb")
def geo():
    """Update version of the used Maxmind geodb, and update the geo IP
    information for each existing server."""
    update_geodb()

@main.command()
@click.argument("socks5_ids", nargs=-1, required=False, type=click.INT)
@click.option("--everything", is_flag=True, help="Delete all socks5 servers")
def delete(socks5_ids, everything):
    """Remove the specified socks5 servers."""
    if socks5_ids:
        for socksid in socks5_ids:
            log.info("Deleting socks5 server with id: %s", socksid)
            try:
                m.delete(socks5_id=socksid)
            except Socks5manError as e:
                log.error("Error deleting socks5 id %s. Error: %s", e)

    elif everything:
        try:
            m.delete_all()
        except Socks5manError as e:
            log.error("Error deleting all socks5 server: %s", e)
            sys.exit(1)

        log.info("Removed all socks5 servers")

@main.command()
@click.option("--country", help="Filtery by the country of a socks5 ip")
@click.option("--code", help="Filter by the 2-letter country code")
@click.option("--city", help="Filter by the city of a socks5 ip")
@click.option("--host", help="Filtery by a hostname/ip")
@click.option("--operational", is_flag=True, help="Only export socks5 servers that were tested to be operational")
@click.option("--export", type=click.Path(), help="Export as CSV to given file path")
def list(country, code, city, host, operational, export):
    """List or export all socks5 servers."""
    if not operational:
        operational = None

    socks5s = m.list_socks5(
        country=country, country_code=code, city=city,
        host=host, operational=operational
    )

    if not socks5s:
        log.warning("No (matching) socks5 servers found")
        sys.exit(1)

    if not export:
        print(
            "{:<4} {:<20} {:<5} {:<16} {:<12} {:<16} {:<16} {:<16}".format(
                "ID", "Host", "Port", "Country", "Country Code", "City",
                "Username", "Password"
            )
        )
        for socks5 in socks5s:
            print(
                "{:<4} {:<20} {:<5} {:<16} {:<12} {:<16} {:<16} {:<16}".format(
                    socks5.id, socks5.host, socks5.port, socks5.country,
                    socks5.country_code, socks5.city, socks5.username,
                    socks5.password
                )
            )
        sys.exit(0)

    if os.path.exists(export):
        log.error("Path '%s' exists", export)
        sys.exit(1)

    with open(export, "wb") as fw:
        csv_w = csv.writer(fw)
        header = True
        for socks5 in socks5s:
            socks5_d = socks5.to_dict()
            if header:
                csv_w.writerow(socks5_d.keys())
                header = False

            csv_w.writerow(socks5_d.values())
