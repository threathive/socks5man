from socks5man.helpers import cwd
from datetime import datetime
import logging

from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Text, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from socks5man.exceptions import Socks5manError

log = logging.getLogger(__name__)

Base = declarative_base()

class Socks5(Base):
    __tablename__ = "socks5s"

    id = Column(Integer(), primary_key=True)
    host = Column(String(255), nullable=False)
    port = Column(Integer(), nullable=False)
    country = Column(String(255), nullable=False)
    country_code = Column(String(2), nullable=False)
    city = Column(String(255), nullable=True)
    username = Column(String(255), nullable=True)
    password = Column(String(255), nullable=True)
    added_on = Column(DateTime(), default=datetime.now, nullable=False)
    last_use = Column(DateTime(), nullable=True)
    last_check = Column(DateTime(), nullable=True)
    operational = Column(Boolean, nullable=False, default=False)
    description = Column(Text(), nullable=True)

    def __init__(self, host, port, country, country_code):
        self.host = host
        self.port = port
        self.country = country
        self.country_code = country_code

    def __repr__(self):
        return "<Socks5(host=%s, port=%s, country=%s, authenticated=%s)>" % (
            self.host, self.port, self.country, (
                self.username is not None and self.password is not None
            )
        )

class Database(object):

    def __init__(self):
        self.connect()

    def connect(self):
        self.engine = create_engine("sqlite:///%s" % cwd("socks5man.db"))
        self.Session = sessionmaker(bind=self.engine)
        self._create()

    def _create(self):
        try:
            Base.metadata.create_all(self.engine)
        except SQLAlchemyError as e:
            raise Socks5manError("Failed to created database tables: %s" % e)

    def __del__(self):
        self.engine.dispose()

    def add_socks5(self, host, port, country, country_code, operational=False,
                   city=None, username=None, password=None, description=None):
        """Add new socks5 server to the database"""
        socks5 = Socks5(host, port, country, country_code)
        socks5.operational = operational
        socks5.city = city
        socks5.username = username
        socks5.password = password
        socks5.description = description

        session = self.Session()
        try:
            session.add(socks5)
            session.commit()
        except SQLAlchemyError as e:
            log.error("Error adding new socks5 to the database: %s", e)
            return False
        finally:
            session.close()
        return True

    def remove_socks5(self, id):
        """Removes the socks5 entry with the specified id"""
        session = self.Session()
        try:
            session.query(Socks5).filter_by(id=id).delete()
            session.commit()
        except SQLAlchemyError as e:
            log.error("Error while removing socks5 from the database: %s", e)
            return False
        finally:
            session.close()
        return True

    def list_socks5(self, country=None, country_code=None, city=None,
                    limit=500):

        session = self.Session()
        socks = session.query(Socks5)
        try:
            if country:
                socks = socks.filter_by(country=country)
            if country_code:
                socks = socks.filter_by(country_code=country_code)
            if city:
                socks = socks.filter_by(city=city)
            socks = socks.limit(limit).all()
            return socks
        except SQLAlchemyError as e:
            log.error("Error retrieving list of socks5s: %s", e)
            return []
        finally:
            session.close()

    def bulk_add_socks5(self, socks5_dict_list):
        """Bulk insert multiple socks5s
        @param socks5_dict_list: A list of dictionaries containing
        all filled in columns for each socks5 entry"""
        try:
            self.engine.execute(Socks5.__table__.insert(), socks5_dict_list)
            return True
        except SQLAlchemyError as e:
            log.error("Error bulk adding socks5 to database: %s", e)
            return False
