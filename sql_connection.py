from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
class Listing(Base):
    __tablename__ = 'listings'
    
    id = Column(Integer, primary_key=True, unique=True)
    link = Column(String, unique=True)
    created = Column(DateTime)
    latitude = Column(Float)
    longitude = Column(Float)
    name = Column(String)
    price = Column(Float)
    location = Column(String)
    area = Column(String)
    cta_stop = Column(String)


class ApartmentsSqlConnection:
    def __init__(self):
        self.engine = create_engine('sqlite:///listings.db', echo=False)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        Base.metadata.create_all(self.engine)
        