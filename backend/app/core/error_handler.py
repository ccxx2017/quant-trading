# app/core/error_handler.py
import logging
import asyncio
from typing import Callable, Any
from functools import wraps
from datetime import datetime
from app.core.exceptions import DataFetchError, DatabaseError
from app.core.config import settings

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"logs/stock_data_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def handle_data_errors(retries: int = 3, delay: int = 1):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            for attempt in range(retries):
                try:
                    if asyncio.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    return func(*args, **kwargs)
                except DataFetchError as e:
                    logger.error(f"Data fetch error: {str(e)}, attempt {attempt + 1}/{retries}")
                    if attempt == retries - 1:
                        raise
                    await asyncio.sleep(delay * (attempt + 1))
                except DatabaseError as e:
                    logger.error(f"Database error: {str(e)}, attempt {attempt + 1}/{retries}")
                    if attempt == retries - 1:
                        raise
                    await asyncio.sleep(delay * (attempt + 1))
                except Exception as e:
                    logger.error(f"Unexpected error: {str(e)}")
                    raise
        return wrapper
    return decorator