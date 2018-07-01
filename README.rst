Socks5man is a Socks5 management tool and Python library. It
enables you to add socks5 servers, run a service that verifies if
they are operational, and request these servers in a round-robin fashion
by country, city, average connection time, and bandwidth, using the Python library.

The library also allows for manual operationality, bandwidth, and connection time tests.
A local database is used to lookup country and city information for a host ip.

The documentation can be found at: `https://socks5man.readthedocs.io`_.

This product includes GeoLite2 data created by MaxMind, available from `maxmind.com`_.

.. image:: https://api.travis-ci.org/RicoVZ/socks5man.svg?branch=master
   :alt: Linux and OSX Build Status
   :target: https://travis-ci.org/RicoVZ/socks5man

.. image:: https://ci.appveyor.com/api/projects/status/le7o92n6t1glv4su?svg=true
   :alt: Windows Build Status
   :target: https://ci.appveyor.com/project/RicoVZ/socks5man

.. image:: https://codecov.io/gh/ricovz/socks5man/branch/master/graph/badge.svg
   :alt: Codecov Coverage Status
   :target: https://codecov.io/gh/RicoVZ/socks5man

.. _`maxmind.com`: http://www.maxmind.com
.. _`https://socks5man.readthedocs.io`: https://socks5man.readthedocs.io/
