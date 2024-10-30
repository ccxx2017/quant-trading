# app/models/stock.py
from sqlalchemy import Column, String, DateTime
from app.core.database import Base
from datetime import datetime

class Stock(Base):
    __tablename__ = "stocks"
    
    ts_code = Column(String, primary_key=True)
    symbol = Column(String)
    name = Column(String)
    area = Column(String)
    industry = Column(String)
    list_date = Column(String)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)