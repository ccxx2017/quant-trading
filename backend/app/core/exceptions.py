# app/core/exceptions.py
class DataFetchError(Exception):
    """数据获取错误"""
    pass

class DatabaseError(Exception):
    """数据库操作错误"""
    pass