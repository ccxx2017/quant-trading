from sqlalchemy import Column, String, Float, DateTime, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Stock(Base):
    __tablename__ = 'stock_basic'

    ts_code = Column(String(10), primary_key=True)
    symbol = Column(String(10))
    name = Column(String(50))
    area = Column(String(50))
    industry = Column(String(50))
    list_date = Column(String(8))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    daily_data = relationship("DailyData", back_populates="stock")

class DailyData(Base):
    __tablename__ = "daily_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_code = Column(String(10), ForeignKey('stock_basic.ts_code'), nullable=False)
    trade_date = Column(String(8), nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    amount = Column(Float)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    stock = relationship("Stock", back_populates="daily_data")

    __table_args__ = (
        UniqueConstraint('stock_code', 'trade_date', name='uix_stock_trade_date'),
        {'extend_existing': True}
    )