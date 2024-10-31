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
from app.models import Stock, DailyData
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

    @handle_data_errors(retries=3)
    async def update_stock_basics(self):
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
    async def update_daily_data(self):
        """更新日线数据"""
        try:
            logger.info("Starting to update daily data...")
            # 获取所有股票代码
            stocks = self.db.query(Stock).all()
            if not stocks:
                logger.warning("No stocks found in database")
                return False

            success_count = 0
            error_count = 0

            for stock in stocks:
                try:
                    # 获取日线数据
                    end_date = datetime.now().strftime('%Y%m%d')
                    start_date = (datetime.now() - timedelta(days=5)).strftime('%Y%m%d')
                    
                    logger.info(f"Fetching daily data for {stock.ts_code}")
                    df = self.ts_api.daily(
                        ts_code=stock.ts_code,
                        start_date=start_date,
                        end_date=end_date
                    )
                    
                    if df is None or df.empty:
                        logger.warning(f"No daily data found for stock {stock.ts_code}")
                        continue

                    # 更新数据库
                    for _, row in df.iterrows():
                        try:
                            # 检查是否存在
                            existing_data = self.db.query(DailyData).filter(
                                DailyData.stock_code == row['ts_code'],
                                DailyData.trade_date == row['trade_date']
                            ).first()

                            if existing_data:
                                # 更新现有记录
                                existing_data.open = row['open']
                                existing_data.high = row['high']
                                existing_data.low = row['low']
                                existing_data.close = row['close']
                                existing_data.volume = row['vol']
                                existing_data.amount = row['amount']
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

                            success_count += 1
                        except Exception as e:
                            error_count += 1
                            logger.error(f"Error processing daily data for {stock.ts_code} on {row['trade_date']}: {str(e)}")
                            continue
                    
                    await asyncio.sleep(0.2)  # 避免触发频率限制
                    
                except Exception as e:
                    logger.error(f"Error updating daily data for stock {stock.ts_code}: {str(e)}")
                    continue

            # 提交所有更改
            self.db.commit()
            logger.info(f"Successfully updated daily data. "
                       f"Processed: {success_count + error_count}, "
                       f"Success: {success_count}, "
                       f"Errors: {error_count}")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update daily data: {str(e)}")
            raise DataFetchError(f"Failed to update daily data: {str(e)}")

    async def get_stock_list(self) -> List[Dict]:
        """获取股票列表"""
        try:
            logger.info("Fetching stock list...")
            stocks = self.db.query(Stock).all()
            return [stock.to_dict() for stock in stocks]
        except Exception as e:
            logger.error(f"Failed to get stock list: {str(e)}")
            raise DatabaseError(f"Failed to get stock list: {str(e)}")