# app/services/data_consistency.py
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Stock
from app.models.stock import DailyData
from app.core.database import get_db
import pandas as pd

class DataConsistencyService:
    def __init__(self):
        self.db: Session = next(get_db())
    
    async def verify_data_integrity(self, 
                                  stock_code: str, 
                                  start_date: datetime, 
                                  end_date: datetime) -> bool:
        # 检查数据连续性
        daily_data = self.db.query(DailyData).filter(
            DailyData.stock_code == stock_code,
            DailyData.trade_date.between(
                start_date.strftime('%Y%m%d'), 
                end_date.strftime('%Y%m%d')
            )
        ).all()
        
        # 验证数据完整性
        return self._check_data_sequence(daily_data)
    
    def _check_data_sequence(self, data: List[DailyData]) -> bool:
        if not data:
            return False
        
        # 转换为pandas DataFrame进行时间序列分析
        df = pd.DataFrame([{
            'trade_date': item.trade_date,
            'stock_code': item.stock_code
        } for item in data])
        
        if df.empty:
            return False
            
        # 检查时间间隔是否符合预期
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        df = df.sort_values('trade_date')
        date_diffs = df['trade_date'].diff().dropna()
        
        return all(diff <= timedelta(days=3) for diff in date_diffs)