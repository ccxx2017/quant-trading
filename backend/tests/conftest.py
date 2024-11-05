import os
import sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# 设置项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


from app.models.base import Base
from app.core.database import get_db


# 测试数据库配置
TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="function")
def test_db():
    # 创建测试数据库引擎
    engine = create_engine(TEST_DATABASE_URL)
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    # 创建会话
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # 提供测试数据库会话
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()
        # 清理测试数据库
        Base.metadata.drop_all(bind=engine)