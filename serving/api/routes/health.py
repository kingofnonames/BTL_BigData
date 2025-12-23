from fastapi import APIRouter, Depends
from models.responses import HealthResponse
from api.dependencies import get_es_service, get_redis_service

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("", response_model=HealthResponse)
async def health_check(
    es=Depends(get_es_service),
    redis=Depends(get_redis_service)
):
    es_healthy = es.health_check()
    redis_healthy = redis.health_check()
    
    return HealthResponse(
        status="healthy" if all([es_healthy, redis_healthy]) else "degraded",
        elasticsearch=es_healthy,
        redis=redis_healthy
    )

@router.get("/ping")
async def ping():
    return {"status": "ok", "message": "pong"}

@router.get("/detailed")
async def detailed_health(
    es=Depends(get_es_service),
    redis=Depends(get_redis_service)
):
    """Detailed health check with configuration info"""
    return {
        "status": "healthy",
        "elasticsearch": {
            "connected": es.health_check(),
            "host": es.host,
            "batch_indexes": {
                "ohlcv": es.index_ohlcv,
                "analysis": es.index_analysis,
                "market": es.index_market,
                "market_analysis": es.index_market_analysis
            },
            "speed_indexes": {
                "ohlcv": es.index_ohlcv_speed,
                "analysis": es.index_analysis_speed,
                "market": es.index_market_speed,
                "market_analysis": es.index_market_analysis_speed
            },
            "speed_enabled": es.speed_enabled
        },
        "redis": {
            "connected": redis.health_check(),
            "host": f"{redis.host}:{redis.port}",
            "ttl_config": {
                "latest_price": redis.ttl_latest,
                "indicators": redis.ttl_indicators,
                "market": redis.ttl_market,
                "market_indicators": redis.ttl_market_indicators
            }
        }
    }

@router.post("/cache/clear")
async def clear_all_cache(redis=Depends(get_redis_service)):
    """Clear all cache - use with caution"""
    try:
        count = 0
        patterns = [
            "latest:*",
            "indicators:*",
            "market:latest:*",
            "market:indicators:*",
            "market:compare:*"
        ]
        
        for pattern in patterns:
            keys = redis.client.keys(pattern)
            if keys:
                count += redis.client.delete(*keys)
        
        return {"success": True, "keys_deleted": count}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/cache/clear/{symbol}")
async def clear_symbol_cache(
    symbol: str,
    redis=Depends(get_redis_service)
):
    """Clear cache for specific symbol or market index"""
    symbol = symbol.upper()
    count = 0
    
    # Stock cache keys
    stock_keys = [
        f"latest:{symbol}",
        f"indicators:{symbol}"
    ]
    
    # Market cache keys (if symbol is a market index)
    market_keys = [
        f"market:latest:{symbol}",
        f"market:indicators:{symbol}"
    ]
    
    all_keys = stock_keys + market_keys
    
    for key in all_keys:
        if redis.client.exists(key):
            redis.client.delete(key)
            count += 1
    
    return {"symbol": symbol, "keys_deleted": count}

@router.get("/cache/stats")
async def cache_statistics(redis=Depends(get_redis_service)):
    """Get cache statistics"""
    try:
        info = redis.client.info("stats")
        
        # Count keys by pattern
        stock_latest = len(redis.client.keys("latest:*"))
        stock_indicators = len(redis.client.keys("indicators:*"))
        market_latest = len(redis.client.keys("market:latest:*"))
        market_indicators = len(redis.client.keys("market:indicators:*"))
        market_compare = len(redis.client.keys("market:compare:*"))
        
        return {
            "total_keys": info.get("db0", {}).get("keys", 0),
            "keys_by_type": {
                "stock_latest": stock_latest,
                "stock_indicators": stock_indicators,
                "market_latest": market_latest,
                "market_indicators": market_indicators,
                "market_compare": market_compare
            },
            "hits": info.get("keyspace_hits", 0),
            "misses": info.get("keyspace_misses", 0),
            "hit_rate": round(
                info.get("keyspace_hits", 0) / 
                max(info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1) * 100,
                2
            )
        }
    except Exception as e:
        return {"error": str(e)}