from setuptools import setup

setup(
    name="Socks5man",
    version="0.1",
    author="Ricardo van Zutphen",
    packages=[
        "socks5man",
    ],
    license="GPLv3",
    description="SOCKS5 server management tool and library",
    include_package_data=True,
    install_requires=[
        "PySocks==1.5.7",
        "geoip2==2.8.0",
        "SQLAlchemy==1.2.7",
        "click==6.6"
    ],
    python_requires="<=2.7",
    extras_require={
        ":sys_platform == 'win32'": [
            "win-inet-pton==1.0.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "socks5man = socks5man.main:main"
        ],
    }
)
