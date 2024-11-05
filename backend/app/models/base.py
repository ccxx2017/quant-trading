from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase

# 使用新的方式创建 Base 类
class Base(DeclarativeBase):
    pass