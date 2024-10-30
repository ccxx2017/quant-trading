# app/services/stock_service.py
import tushare as ts
from sqlalchemy.orm import Session
from app.models.stock import Stock
from app.core.config import settings

class StockService:
    def __init__(self):
        self.pro = ts.pro_api(settings.TUSHARE_TOKEN)
    
    async def fetch_stock_basics(self) -> dict:
        """获取股票基础信息"""
        try:
            df = self.pro.stock_basic(
                exchange='',
                list_status='L',
                fields='ts_code,symbol,name,area,industry,list_date'
            )
            return {"status": "success", "data": df.to_dict('records')}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def save_stocks(self, db: Session, stocks_data: list):
        """保存股票数据到数据库"""
        try:
            for stock_data in stocks_data:
                stock = Stock(**stock_data)
                db.merge(stock)  # 使用merge代替add，实现更新或插入
            db.commit()
            return {"status": "success", "message": f"Saved {len(stocks_data)} stocks"}
        except Exception as e:
            db.rollback()
            return {"status": "error", "message": str(e)}