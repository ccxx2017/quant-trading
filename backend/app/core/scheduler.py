# app/core/scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.services.stock_service import StockService

class StockDataScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        # 不在初始化时创建 StockService
        
    async def setup_jobs(self):
        # 每个交易日9:30-15:00期间每分钟更新
        self.scheduler.add_job(
            self._update_stock_basics,  # 使用类方法
            CronTrigger(
                day_of_week='mon-fri', 
                hour='9-15', 
                minute='*',
                second='0'
            ),
            id='update_stock_basics',
            misfire_grace_time=30
        )
        
        # 每日收盘后更新日线数据
        self.scheduler.add_job(
            self._update_daily_data,  # 使用类方法
            CronTrigger(
                day_of_week='mon-fri',
                hour='15',
                minute='30'
            ),
            id='update_daily_data'
        )

    async def _update_stock_basics(self):
        """包装更新方法"""
        stock_service = StockService()
        await stock_service.update_stock_basics()

    async def _update_daily_data(self):
        """包装更新方法"""
        stock_service = StockService()
        await stock_service.update_daily_data()

    def start(self):
        self.scheduler.start()

    def shutdown(self):
        self.scheduler.shutdown()