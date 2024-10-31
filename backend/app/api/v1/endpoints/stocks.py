# app/api/v1/endpoints/stocks.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict

from app.core.database import get_db
from app.services.stock_service import StockService
from app.models.stock import StockBasic as Stock  # 将 StockBasic 别名为 Stock

router = APIRouter()
stock_service = StockService()

@router.get("/stocks/", response_model=List[Dict])
async def get_stocks(db: Session = Depends(get_db)):
    """获取股票列表"""
    return await stock_service.get_stock_list()

@router.get("/stocks/{stock_code}")
async def get_stock(stock_code: str, db: Session = Depends(get_db)):
    """获取单个股票信息"""
    try:
        stock = db.query(Stock).filter(Stock.ts_code == stock_code).first()
        if stock is None:
            raise HTTPException(status_code=404, detail="Stock not found")
        return stock.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stocks/update")
async def update_stocks():
    """更新股票基础数据"""
    try:
        result = await stock_service.update_stock_basics()
        return {"message": "Stock data updated successfully", "status": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stocks/daily/update")
async def update_daily_data():
    """更新股票日线数据"""
    try:
        result = await stock_service.update_daily_data()
        return {"message": "Daily data updated successfully", "status": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))