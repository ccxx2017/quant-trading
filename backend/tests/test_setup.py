# tests/test_setup.py
import pytest
import asyncio
import logging
import sys
import os
import logging
from datetime import datetime, timedelta
from sqlalchemy import text

# 获取项目根目录的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
# 将项目根目录添加到Python路径
sys.path.insert(0, project_root)

from app.models.stock import DailyData
from app.core.config import settings
from app.core.database import get_db, init_db, engine
from app.core.scheduler import StockDataScheduler
from app.services.stock_service import StockService
from app.services.data_consistency import DataConsistencyService
from app.models.stock import Base


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def clear_database():
    """清空数据库"""
    print("Clearing database...")
    try:
        # 使用正确的方式执行 SQL
        with engine.connect() as conn:
            conn.execute(text("DROP INDEX IF EXISTS ix_daily_data_stock_code"))
            conn.commit()
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        print("✓ Database cleared successfully")
    except Exception as e:
        print(f"✗ Failed to clear database: {str(e)}")
        logger.error(f"Database clearing failed: {str(e)}")
        raise e

@pytest.mark.asyncio
async def test_system():
    """测试系统功能"""
    print("=== 系统测试开始 ===")
    
    # 0. 清空并初始化数据库
    print("\n0. 初始化数据库...")
    await clear_database()
    
    # 1. 测试数据库连接
    print("\n1. 测试数据库连接...")
    print("\n1. 测试数据库连接...")
    db = next(get_db())
    assert db is not None, "数据库连接失败"
    print("✓ 数据库连接成功")

    # 2. 测试 Tushare 连接和数据获取
    print("\n2. 测试 Tushare 连接和数据获取...")
    stock_service = StockService()
    try:
        # 2.1 测试基础连接
        test_stock = stock_service.ts_api.stock_basic(
            ts_code='000001.SZ,000002.SZ,000003.SZ,000004.SZ,000005.SZ'
        )
        print("✓ Tushare 连接成功")
        print(f"示例数据: {test_stock.head(1)}")
        logger.info("Tushare connection successful")
        
        # 2.2 测试基础数据更新
        await stock_service.update_stock_basics()
        logger.info("Basic stock data updated successfully")
        print("✓ 基础数据保存成功")
        
        # 2.3 测试批量数据获取
        # 使用较短的回溯期进行测试
        test_backtrack_days = 5
        await stock_service.update_daily_data(backtrack_days=test_backtrack_days)
        print("✓ 批量数据获取成功")
        logger.info(f"Daily data updated successfully with {test_backtrack_days} days backtrack")
        
        # 2.4 验证数据是否正确保存
        db = next(get_db())
        daily_count = db.query(DailyData).count()
        print(f"✓ 已保存 {daily_count} 条日线数据")
        logger.info(f"Saved {daily_count} daily records")
        
    except Exception as e:
        print(f"✗ Tushare 测试失败: {str(e)}")
        logger.error(f"Tushare test failed: {str(e)}")
        return

    # 3. 测试调度器
    print("\n3. 测试调度器...")
    try:
        scheduler = StockDataScheduler()
        await scheduler.setup_jobs()
        scheduler.start()
        print("✓ 调度器启动成功")
        logger.info("Scheduler started successfully")
        
        # 运行几秒后关闭
        await asyncio.sleep(5)
        scheduler.shutdown()
        print("✓ 调度器关闭成功")
        logger.info("Scheduler shutdown successfully")
    except Exception as e:
        print(f"✗ 调度器测试失败: {str(e)}")
        logger.error(f"Scheduler test failed: {str(e)}")

    # 4. 测试数据一致性服务
    print("\n4. 测试数据一致性服务...")
    try:
        # 先确保有测试数据
        await stock_service.update_daily_data()
        logger.info("Daily data updated for consistency check")
        
        consistency_service = DataConsistencyService()
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        result = await consistency_service.verify_data_integrity(
            "000001.SZ", 
            start_date,
            end_date
        )
        print(f"✓ 数据一致性检查完成，结果: {result}")
        logger.info(f"Data consistency check completed with result: {result}")
    except Exception as e:
        print(f"✗ 数据一致性服务测试失败: {str(e)}")
        logger.error(f"Data consistency test failed: {str(e)}")

    print("\n=== 系统测试完成 ===")

# 运行测试
if __name__ == "__main__":
    try:
        asyncio.run(test_system())
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        logger.info("Test interrupted by user")
    except Exception as e:
        print(f"\n测试过程中发生错误: {str(e)}")
        logger.error(f"Test failed with error: {str(e)}")