Installation and configuration
==============================

**This page is a work in progress. More information will be added. Be back soon!**

Installation
------------

It is recommended that socks5man is installed in a virtualenv.

Install Socks5man as follows::

    $ virtualenv venv
    $ source venv/bin/activate
    (venv)$ pip install -U socks5man

After installing, run Socks5man once to created its working directory (.socks5man) in your user home::

    (venv)$ socks5man
    Usage: socks5man [OPTIONS] COMMAND [ARGS]...

      This tool can be used to manage your socks5
      servers. Each subcommand has its own help
      information.

    Options:
      -d, --debug  Enable debug logging
      --help       Show this message and exit.

    Commands:
      add           Add socks5 server.
      bulk-add      Bulk add socks5 servers from CSV file.
      delete        Remove the specified socks5 servers.
      list          List or export all socks5 servers.
      update-geodb  Update version of the used Maxmind geodb, and...
      verify        Verify if the servers are operational.

After installing and running Socks5man once, its working directory will have been created. This directory contains
the configuration file (socks5man.conf), the geolite2 database, and the socks5man database. The latter is the database that stores
all the socks5 server information.

	  
.. toctree::
