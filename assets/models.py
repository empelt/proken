# coding: utf-8


from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Text
from assets.database import Base
from datetime import datetime as dt

class Data(Base):
    __tablename__ = "data"
    id = Column(Integer, primary_key=True)
    count = Column(Integer, unique=False)
    timestamp = Column(DateTime, unique=False)

    def __init__(self, count=0, timestamp=None):
        self.count = count
        self.timestamp = timestamp
