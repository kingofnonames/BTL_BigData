import redis
import json
import logging
import os
from typing import Optional, Any

logger = logging.getLogger(__name__)

class RedisService:
    def __init__(self):
        self.host = os.getenv("REDIS_HOST", "redis")
        self.port = int(os.getenv("REDIS_PORT", "6379"))
        
        # TTL configurations
        self.ttl_latest = int(os.getenv("CACHE_TTL_LATEST", "60"))
        self.ttl_historical = int(os.getenv("CACHE_TTL_HISTORICAL", "3600"))
        self.ttl_indicators = int(os.getenv("CACHE_TTL_INDICATORS", "300"))
        self.ttl_market = int(os.getenv("CACHE_TTL_MARKET", "60"))  # Same as latest price
        self.ttl_market_indicators = int(os.getenv("CACHE_TTL_MARKET_INDICATORS", "300"))
        
        self.client = redis.Redis(
            host=self.host,
            port=self.port,
            decode_responses=True,
            socket_connect_timeout=5
        )
        
        try:
            self.client.ping()
            logger.info(f"Connected to Redis: {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Redis connection error: {e}")
    
    # =============================================
    # GENERIC CACHE METHODS
    # =============================================
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis GET error for {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        try:
            serialized = json.dumps(value, default=str)
            if ttl:
                self.client.setex(key, ttl, serialized)
            else:
                self.client.set(key, serialized)
            return True
        except Exception as e:
            logger.error(f"Redis SET error for {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key"""
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis DELETE error: {e}")
            return False
    
    # =============================================
    # STOCK OHLCV CACHE METHODS
    # =============================================
    
    def cache_latest_price(self, symbol: str, data: dict) -> bool:
        key = f"latest:{symbol}"
        return self.set(key, data, self.ttl_latest)
    
    def get_latest_price(self, symbol: str) -> Optional[dict]:
        key = f"latest:{symbol}"
        return self.get(key)
    
    def cache_indicators(self, symbol: str, data: dict) -> bool:
        key = f"indicators:{symbol}"
        return self.set(key, data, self.ttl_indicators)
    
    def get_indicators(self, symbol: str) -> Optional[dict]:
        key = f"indicators:{symbol}"
        return self.get(key)
    
    # =============================================
    # MARKET INDEX CACHE METHODS
    # =============================================
    
    def cache_latest_market(self, index_code: str, data: dict) -> bool:
        """Cache latest market index data"""
        key = f"market:latest:{index_code}"
        return self.set(key, data, self.ttl_market)
    
    def get_latest_market(self, index_code: str) -> Optional[dict]:
        """Get cached latest market index data"""
        key = f"market:latest:{index_code}"
        return self.get(key)
    
    def cache_market_indicators(self, index_code: str, data: dict) -> bool:
        """Cache market indicators"""
        key = f"market:indicators:{index_code}"
        return self.set(key, data, self.ttl_market_indicators)
    
    def get_market_indicators(self, index_code: str) -> Optional[dict]:
        """Get cached market indicators"""
        key = f"market:indicators:{index_code}"
        return self.get(key)
    
    def cache_market_compare(self, indices_key: str, data: dict) -> bool:
        """Cache market comparison data"""
        key = f"market:compare:{indices_key}"
        return self.set(key, data, self.ttl_market)
    
    def get_market_compare(self, indices_key: str) -> Optional[dict]:
        """Get cached market comparison"""
        key = f"market:compare:{indices_key}"
        return self.get(key)
    
    # =============================================
    # UTILITY METHODS
    # =============================================
    
    def health_check(self) -> bool:
        try:
            return self.client.ping()
        except:
            return False