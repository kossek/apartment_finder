from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
class ApartmentsDb(Base):
    __tablename__ = 'apartments'
    
    id = Column(Integer, primary_key=True)
    link = Column(String, unique=True)
    created = Column(DateTime)
    geotag = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    name = Column(String)
    price = Column(Float)
    location = Column(String)
    cl_id = Column(Integer, unique=True)
    area = Column(String)
    cta_stop = Column(String)


class ApartmentsSqlConnection:
    def __init__(self):
        engine = create_engine('sqlite:///listings.db', echo=False)
        Session = sessionmaker(bind=engine)
        session = Session()
        Base.metadata.create_all(engine)
        