import sys

from setuptools import setup

if sys.version[0] != "2":
    sys.exit(
        "Socks5man currently only supports Python 2.7. 3.5+ is on the roadmap"
        ", but is not supported yet. For now, please install it in the"
        " following way: `pip2 install -U socks5man`."
    )

setup(
    name="Socks5man",
    version="0.1.1",
    author="Ricardo van Zutphen",
    author_email="ricardo@cuckoo.sh",
    packages=[
        "socks5man",
    ],
    keywords="socks5man socks5 tester management library verification",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Topic :: System :: Monitoring",
        "Topic :: Security",
    ],
    license="GPLv3",
    description="SOCKS5 server management tool and library",
    long_description=open("README.rst", "rb").read(),
    include_package_data=True,
    url="https://github.com/RicoVZ/socks5man",
    install_requires=[
        "PySocks==1.5.7",
        "geoip2==2.8.0",
        "SQLAlchemy>=1.0.8, <=1.2.7",
        "click==6.6"
    ],
    python_requires=">=2.7, <3.0",
    extras_require={
        ":sys_platform == 'win32'": [
            "win-inet-pton==1.0.1",
        ],
    },
    tests_require=[
        "pytest",
        "mock"
    ],
    entry_points={
        "console_scripts": [
            "socks5man = socks5man.main:main"
        ],
    }
)
