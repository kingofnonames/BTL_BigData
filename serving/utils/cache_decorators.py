from functools import wraps
import hashlib
import json
from typing import Callable

def cache_key(*args, **kwargs) -> str:
    """Generate cache key from function arguments"""
    key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
    return hashlib.md5(key_data.encode()).hexdigest()

def redis_cache(ttl: int = 300, key_prefix: str = "cache"):
    """
    Redis cache decorator
    
    Usage:
    @redis_cache(ttl=60, key_prefix="price")
    async def get_price(symbol: str):
        ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get redis from kwargs if passed
            redis_service = kwargs.get('redis')
            
            if not redis_service:
                # No redis, just call function
                return await func(*args, **kwargs)
            
            # Generate cache key
            cache_k = f"{key_prefix}:{cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached = redis_service.get(cache_k)
            if cached is not None:
                return cached
            
            # Call function
            result = await func(*args, **kwargs)
            
            # Store in cache
            if result is not None:
                redis_service.set(cache_k, result, ttl)
            
            return result
        
        return wrapper
    return decorator