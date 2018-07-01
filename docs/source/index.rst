=======================
Socks5man documentation
=======================

Socks5man is a Socks5 management tool and Python library. It enables you to add socks5 servers, run a service that verifies if they are operational, and request these servers in a round-robin fashion by country, city, average connection time, and bandwidth, using the Python library or command line tools.

The library also allows for manual operationality, bandwidth, and connection time tests. A local database is used to lookup country and city information for a host ip.

Socks5man uses a Geolite2 database provided by MaxMind to perform IP to country and city lookups.

Socks5man consists of command line tools and a Python package containing management helpers that can be used in your scripts/programs.
These allow you to add, test, list, export, and remove socks5 servers to its database.

Want to use socks5man in your script/program? See:

* :doc:`pythonpackage/index`

.. toctree::

    installation/index
    commandline/index
    pythonpackage/index
