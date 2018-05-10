import click
import sys

from socks5man.tools import verify_all

@click.group()
@click.option("-d", "--debug", is_flag=True, help="Enable debug logging")
def main(debug):
    print "main app"

@main.command()
@click.option("-s", "--service", is_flag=True, help="Start a service that keeps verifying all servers at the interval specified in the config")
def verify(service):
    """Verify if the servers are operational"""
    try:
        verify_all(service)
    except KeyboardInterrupt:
        print "CTRL+C detected! exiting."
        sys.exit(0)
