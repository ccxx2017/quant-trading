# app/api/v1/endpoints/stocks.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.stock_service import StockService
from app.models.stock import Stock

router = APIRouter()
stock_service = StockService()

@router.post("/update_basics")
async def update_stock_basics(db: Session = Depends(get_db)):
    """手动更新股票基础数据"""
    # 获取数据
    result = await stock_service.fetch_stock_basics()
    if result["status"] == "error":
        return result
    
    # 保存数据
    return await stock_service.save_stocks(db, result["data"])

@router.get("/list")
async def get_stock_list(db: Session = Depends(get_db)):
    """获取股票列表"""
    stocks = db.query(Stock).all()
    return {"status": "success", "data": [s.__dict__ for s in stocks]}