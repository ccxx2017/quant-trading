# app/services/stock_service.py
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import asyncio
import pandas as pd
from sqlalchemy.orm import Session
from app.core.error_handler import handle_data_errors
from app.services.data_consistency import DataConsistencyService
from app.core.database import get_db
from app.models import Stock
from app.models.stock import DailyData
from app.core.config import settings
import tushare as ts
from app.core.exceptions import DataFetchError, DatabaseError

# 配置日志
logger = logging.getLogger(__name__)

class StockService:
    def __init__(self):
        self.data_consistency = DataConsistencyService()
        self.db: Session = next(get_db())
        self.ts_api = ts.pro_api(settings.TUSHARE_TOKEN)
        # Configuration parameters
        self.BATCH_SIZE = 50  
        self.QUERY_LIMIT = 500
        self.SINGLE_QUERY_LIMIT = 6000
        self.DEFAULT_BACKTRACK_DAYS = settings.DEFAULT_BACKTRACK_DAYS

    def _split_time_ranges(self, start_date: str, end_date: str) -> List[tuple]:
        """将时间范围分割为适合单次查询的片段"""
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        
        # 计算每个分片的天数（考虑单次查询限制）
        days_per_query = self.SINGLE_QUERY_LIMIT // self.BATCH_SIZE
        
        time_ranges = []
        current = start
        while current < end:
            next_date = min(current + timedelta(days=days_per_query), end)
            time_ranges.append((
                current.strftime('%Y%m%d'),
                next_date.strftime('%Y%m%d')
            ))
            current = next_date + timedelta(days=1)
        
        return time_ranges
    
    async def _process_stock_batch(self, stock_codes: List[str], 
                             start_date: str, end_date: str) -> bool:
        """处理一批股票的数据获取"""
        try:
            # 使用逗号分隔的股票代码字符串
            codes = ','.join(stock_codes)
            
            # 获取数据
            df = self.ts_api.daily(
                ts_code=codes,
                start_date=start_date,
                end_date=end_date
            )
            
            if df is None or df.empty:
                logger.warning(f"No data found for batch {stock_codes}")
                return True
            
            # 批量插入或更新数据
            await self._batch_update_daily_data(df)
            
            return True
        
        except Exception as e:
            logger.error(f"Error processing batch {stock_codes}: {str(e)}")
            return False
        
    @handle_data_errors(retries=3)
    async def update_stock_basics(self,backtrack_days: Optional[int] = None):
        """更新股票基础数据"""
        try:
            logger.info("Starting to update stock basics...")
            # 获取股票基本信息
            df = self.ts_api.stock_basic(
                # exchange='',
                # list_status='L',
                # fields='ts_code,symbol,name,area,industry,list_date'
                ts_code='000001.SZ,000002.SZ,000003.SZ,000004.SZ,000005.SZ',
                fields='ts_code,symbol,name,area,industry,list_date'
            )
            
            success_count = 0
            error_count = 0
            
            # 更新数据库
            for _, row in df.iterrows():
                try:
                    # 首先检查是否存在
                    existing_stock = self.db.query(Stock).filter(
                        Stock.ts_code == row['ts_code']
                    ).first()
                    
                    if existing_stock:
                        # 更新现有记录
                        existing_stock.symbol = row['symbol']
                        existing_stock.name = row['name']
                        existing_stock.area = row['area']
                        existing_stock.industry = row['industry']
                        existing_stock.list_date = row['list_date']
                        existing_stock.updated_at = datetime.now()
                    else:
                        # 创建新记录
                        new_stock = Stock(
                            ts_code=row['ts_code'],
                            symbol=row['symbol'],
                            name=row['name'],
                            area=row['area'],
                            industry=row['industry'],
                            list_date=row['list_date']
                        )
                        self.db.add(new_stock)
                    
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    logger.error(f"Error processing stock {row['ts_code']}: {str(e)}")
                    continue
            
            # 提交所有更改
            self.db.commit()
            
            logger.info(f"Successfully updated stock basics. "
                       f"Processed: {success_count + error_count}, "
                       f"Success: {success_count}, "
                       f"Errors: {error_count}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update stock basics: {str(e)}")
            raise DataFetchError(f"Failed to update stock basics: {str(e)}")

    @handle_data_errors(retries=3)
    async def update_daily_data(self,backtrack_days:Optional[int]=None):
        """更新日线数据"""
        try:
            logger.info("Starting to update daily data...")
            # 获取所有股票代码
            stocks = self.db.query(Stock).all()
            if not stocks:
                logger.warning("No stocks found in database")
                return False

            # 计算时间范围
            end_date = datetime.now().strftime('%Y%m%d')
            days = backtrack_days or self.DEFAULT_BACKTRACK_DAYS
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
            # 获取时间分片
            time_ranges = self._split_time_ranges(start_date, end_date)
            # 分批处理股票
            total_stocks = len(stocks)
            for i in range(0, total_stocks, self.BATCH_SIZE):
                batch_stocks = stocks[i:i + self.BATCH_SIZE]
                stock_codes = [stock.ts_code for stock in batch_stocks]
                
                # 处理每个时间分片
                for start, end in time_ranges:
                    success = await self._process_stock_batch(stock_codes, start, end)
                    if not success:
                        logger.error(f"Failed to process batch {i//self.BATCH_SIZE + 1}")
                        continue
                    
                    # 频率限制控制
                    await asyncio.sleep(0.12)  # 确保不超过每分钟500次的限制
                    
            logger.info("Successfully completed daily data update")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update daily data: {str(e)}")
            raise DataFetchError(f"Failed to update daily data: {str(e)}")

    async def _batch_update_daily_data(self, df: pd.DataFrame):
        """批量更新日线数据"""
        try:
            for _, row in df.iterrows():
                # 检查是否存在
                existing_data = self.db.query(DailyData).filter(
                    DailyData.stock_code == row['ts_code'],
                    DailyData.trade_date == row['trade_date']
                ).first()
                
                if existing_data:
                    # 更新现有记录
                    for column in ['open', 'high', 'low', 'close', 'vol', 'amount']:
                        setattr(existing_data, column, row[column])
                    existing_data.updated_at = datetime.now()
                else:
                    # 创建新记录
                    new_data = DailyData(
                        stock_code=row['ts_code'],
                        trade_date=row['trade_date'],
                        open=row['open'],
                        high=row['high'],
                        low=row['low'],
                        close=row['close'],
                        volume=row['vol'],
                        amount=row['amount']
                    )
                    self.db.add(new_data)
            
            # 批量提交
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            raise e
    async def get_stock_list(self) -> List[Dict]:
        """获取股票列表"""
        try:
            logger.info("Fetching stock list...")
            stocks = self.db.query(Stock).all()
            return [stock.to_dict() for stock in stocks]
        except Exception as e:
            logger.error(f"Failed to get stock list: {str(e)}")
            raise DatabaseError(f"Failed to get stock list: {str(e)}")