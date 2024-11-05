from fastapi import FastAPI
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine
from app.models import stock
from app.api.v1.endpoints import stocks
from app.api.v1.endpoints import ai
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from tests import test
from app.api.v1.api import api_router 
from app.core.scheduler import StockDataScheduler
# 确保导入所有模型
from app.models.stock import StockBasic


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中需要修改为具体的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Stock Trading System is running"}


# 创建数据库表
stock.Base.metadata.create_all(bind=engine)

app.include_router(stocks.router, prefix=settings.API_V1_STR + "/stocks", tags=["stocks"])
app.include_router(ai.router, prefix=settings.API_V1_STR + "/ai", tags=["ai"])
app.include_router(test.router, prefix=settings.API_V1_STR, tags=["test"])
# 添加静态文件挂载
app.mount("/static", StaticFiles(directory=Path(__file__).parent.parent / "static"), name="static")