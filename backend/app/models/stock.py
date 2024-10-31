# app/models/stock.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class StockBasic(Base):
    __tablename__ = 'stock_basic'

    id = Column(Integer, primary_key=True, index=True)
    ts_code = Column(String(10), unique=True, index=True, nullable=False)
    symbol = Column(String(6), index=True)
    name = Column(String(50))
    area = Column(String(50))
    industry = Column(String(50))
    list_date = Column(String(8))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'ts_code': self.ts_code,
            'symbol': self.symbol,
            'name': self.name,
            'area': self.area,
            'industry': self.industry,
            'list_date': self.list_date
        }

class DailyData(Base):
    __tablename__ = 'daily_data'

    id = Column(Integer, primary_key=True, index=True)
    stock_code = Column(String(10), ForeignKey('stock_basic.ts_code'), index=True)  # 修改为 stock_code
    trade_date = Column(String(8), index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    amount = Column(Float)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'stock_code': self.stock_code,
            'trade_date': self.trade_date,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume,
            'amount': self.amount
        }