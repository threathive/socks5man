import logging
from datetime import datetime

from socks5man.exceptions import Socks5manError, Socks5manDatabaseError
from socks5man.misc import cwd, Singleton

from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Text, create_engine,
    Float, and_, func
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

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
    bandwidth = Column(Float(), nullable=True)
    connect_time = Column(Float(), nullable=True)
    description = Column(Text(), nullable=True)

    def __init__(self, host, port, country, country_code):
        self.host = host
        self.port = port
        self.country = country
        self.country_code = country_code

    def to_dict(self):
        """Converts object to dict.
        @param dt: encode datetime objects
        @return: dict
        """
        socks_dict = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                socks_dict[column.name] = value.strftime("%Y-%m-%d %H:%M:%S")
            elif isinstance(value, (str, basestring)):
                socks_dict[column.name] = value.encode("utf-8")
            else:
                socks_dict[column.name] = value

        return socks_dict

    def __repr__(self):
        return "<Socks5(host=%s, port=%s, country=%s, authenticated=%s)>" % (
            self.host, self.port, self.country, (
                self.username is not None and self.password is not None
            )
        )

class Database(object):

    __metaclass__ = Singleton

    def __init__(self):
        self.connect(create=True)

    def connect(self, create=False):
        self.engine = create_engine("sqlite:///%s" % cwd("socks5man.db"))
        self.Session = sessionmaker(bind=self.engine)
        if create:
            self._create()

    def _create(self):
        try:
            Base.metadata.create_all(self.engine)
        except SQLAlchemyError as e:
            raise Socks5manError("Failed to created database tables: %s" % e)

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
            socks_id = socks5.id
        except SQLAlchemyError as e:
            raise Socks5manDatabaseError(
                "Error adding new socks5 to the database: %s" % e
            )
        finally:
            session.close()

        return socks_id

    def remove_socks5(self, id):
        """Removes the socks5 entry with the specified id"""
        session = self.Session()
        try:
            session.query(Socks5).filter_by(id=id).delete()
            session.commit()
        except SQLAlchemyError as e:
            raise Socks5manDatabaseError(
                "Error while removing socks5 from the database: %s" % e
            )
        finally:
            session.close()

    def list_socks5(self, country=None, country_code=None, city=None,
                    host=None, operational=None):
        """Return a list of socks5 servers matching the filters"""
        session = self.Session()
        socks = session.query(Socks5)
        try:
            if operational is not None:
                socks = socks.filter_by(operational=operational)
            if country:
                socks = socks.filter(
                    func.lower(Socks5.country) == func.lower(country)
                )
            if country_code:
                socks = socks.filter(
                    func.lower(Socks5.country_code) == func.lower(country_code)
                )
            if city:
                socks = socks.filter(
                    func.lower(Socks5.city) == func.lower(city)
                )
            if host:
                if isinstance(host, (list, tuple)):
                    socks = socks.filter(Socks5.host.in_(set(host)))
                else:
                    socks = socks.filter_by(host=host)
            socks = socks.all()
            for s in socks:
                session.expunge(s)

            return socks
        except SQLAlchemyError as e:
            raise Socks5manDatabaseError(
                "Error retrieving list of socks5s: %s" % e
            )
        finally:
            session.close()

    def view_socks5(self, socks5_id=None, host=None, port=None):
        """Returns a socks5 server matching the given id"""
        session = self.Session()
        socks5 = session.query(Socks5)
        try:
            if socks5_id:
                socks5 = socks5.get(socks5_id)
            elif host and port:
                socks5 = socks5.filter(and_(
                    Socks5.host==host, Socks5.port==port
                )).first()
            else:
                raise Socks5manDatabaseError(
                    "Socks5 id or host and port should be provided"
                )

            if socks5:
                session.expunge(socks5)
        except SQLAlchemyError as e:
            raise Socks5manDatabaseError("Error finding socks5: %s" % e)
        finally:
            session.close()
        return socks5

    def find_socks5(self, country=None, country_code=None, city=None,
                    min_mbps_down=None, max_connect_time=None,
                    update_usage=True, limit=1):
        """Find one or more matching socks5 servers matching the provided
        filters. Names etc should be in English
        @param country: The country
        @param country_code: 2 letter country code ISO 3166-1 alpha-2
        @param city: City to filter for
        @param min_mbps_down: Min Mbit/s the server should have (float)
        @param max_connect_time: Max average connection time to
         the server (float)
        @param update_usage: Should the last_used field be updated
         when finding a matching socks5? True by default
        @param limit: The maximum number of socks5s to find and return"""

        result = []
        session = self.Session()
        socks5 = session.query(Socks5)
        try:
            socks5 = socks5.filter_by(operational=True)
            if country:
                socks5 = socks5.filter(
                    func.lower(Socks5.country) == func.lower(country)
                )
            if country_code:
                socks5 = socks5.filter(
                    func.lower(Socks5.country_code) == func.lower(country_code)
                )
            if city:
                socks5 = socks5.filter(
                    func.lower(Socks5.city) == func.lower(city)
                )
            if min_mbps_down:
                socks5 = socks5.filter(Socks5.bandwidth >= min_mbps_down)
            if max_connect_time:
                socks5 = socks5.filter(Socks5.connect_time <= max_connect_time)

            result = socks5.order_by(
                Socks5.last_use.asc(), Socks5.last_check.desc(),
                Socks5.connect_time.asc(), Socks5.bandwidth.desc()
            ).limit(limit).all()

            if result and update_usage:
                for s in result:
                    s.last_use = datetime.now()
                session.commit()

            if result:
                for s in result:
                    if update_usage:
                        session.refresh(s)
                    session.expunge(s)

        except SQLAlchemyError as e:
            raise Socks5manDatabaseError("Error finding socks5: %s" % e)
        finally:
            session.close()

        return result

    def bulk_add_socks5(self, socks5_dict_list):
        """Bulk insert multiple socks5s
        @param socks5_dict_list: A list of dictionaries containing
        all filled in columns for each socks5 entry."""
        try:
            self.engine.execute(Socks5.__table__.insert(), socks5_dict_list)
        except SQLAlchemyError as e:
            raise Socks5manDatabaseError(
                "Error bulk adding socks5 to database: %s" % e
            )

    def set_operational(self, socks5_id, operational):
        """Change the operational status for the given socks5 to the
        given value False/True. The last_check value is automatically
        updated."""
        session = self.Session()
        try:
            socks5 = session.query(Socks5).get(socks5_id)
            if not socks5:
                return
            socks5.operational = operational
            socks5.last_check = datetime.now()
            session.commit()
        except SQLAlchemyError as e:
            raise Socks5manDatabaseError(
                "Error updating operational status in database: %s" % e
            )
        finally:
            session.close()

    def set_connect_time(self, socks5_id, connect_time):
        """Store the approx time it takes to connect to this socks5
        @param connect_time: float representing the connection time."""
        session = self.Session()
        try:
            session.query(Socks5).filter_by(
                id=socks5_id
            ).update({"connect_time": connect_time})
            session.commit()
        except SQLAlchemyError as e:
            raise Socks5manDatabaseError(
                "Error updating connect time in database: %s" % e
            )
        finally:
            session.close()

    def set_approx_bandwidth(self, socks5_id, bandwidth):
        """Store the approximate Mbit/s speed down
        @param bandwidth: float representing the mbit/s speed down."""
        session = self.Session()
        try:
            session.query(Socks5).filter_by(
                id=socks5_id
            ).update({"bandwidth": bandwidth})
            session.commit()
        except SQLAlchemyError as e:
            raise Socks5manDatabaseError(
                "Error updating bandwidth in database: %s" % e
            )
        finally:
            session.close()

    def delete_all_socks5(self):
        """Clear all socks5 server from the database"""
        session = self.Session()
        try:
            session.query(Socks5).delete()
            session.commit()
        except SQLAlchemyError as e:
            raise Socks5manDatabaseError(
                "Failed to delete all socks5 servers: %s" % e
            )
        finally:
            session.close()

    def update_geoinfo(self, socks5_id, country, country_code, city):
        """Update the geoinfo fields for the given socks5 id"""
        session = self.Session()
        try:
            session.query(Socks5).filter_by(id=socks5_id).update({
                "country": country,
                "country_code": country_code,
                "city": city
            })
            session.commit()
        except SQLAlchemyError as e:
            raise Socks5manDatabaseError(
                "Error while updating geo info for socks5 with ID: %s."
                " Error: %s" % (socks5_id, e)
            )
        finally:
            session.close()
