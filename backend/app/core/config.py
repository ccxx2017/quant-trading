from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
import asyncio
from datetime import datetime
import time

load_dotenv()

class Settings(BaseSettings):

    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Quant Trading System"
    
    # SQLite配置
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./quant_trading.db"
    
    TUSHARE_TOKEN: str = os.getenv("TUSHARE_TOKEN")

    ZHIPU_API_KEY: str  = os.getenv("ZHIPU_API_KEY")
    class Config:
        case_sensitive = True


settings = Settings()