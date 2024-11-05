# app/api/v1/endpoints/test.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db

router = APIRouter()

@router.get("/test_db")
def test_database(db: Session = Depends(get_db)):
    try:
        # 使用 text() 包装 SQL 查询
        result = db.execute(text("SELECT 1")).first()
        return {"status": "success", "message": "Database connection successful", "result": result[0]}
    except Exception as e:
        return {"status": "error", "message": str(e)}