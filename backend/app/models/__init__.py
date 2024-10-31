# app/models/__init__.py
from app.models.stock import StockBasic as Stock, DailyData

__all__ = ['Stock', 'DailyData']