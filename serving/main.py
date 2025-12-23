from fastapi import FastAPI
import logging
import os

from api.routes import ohlcv, indicators, predictions, health, market
from utils.logger import setup_logger

# Setup logging
logger = setup_logger("serve_api", os.getenv("LOG_LEVEL", "INFO"))

app = FastAPI(
    title="Stock Serving API",
    version="1.0.0",
    description="Lambda Architecture Serving Layer for Stock Data"
)

# Include routers
app.include_router(health.router, prefix="/api/v1")
app.include_router(ohlcv.router, prefix="/api/v1")
app.include_router(indicators.router, prefix="/api/v1")
app.include_router(predictions.router, prefix="/api/v1")
app.include_router(market.router, prefix="/api/v1")  # NEW: Market indices

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Stock Serving API...")
    logger.info(f"ES_HOST: {os.getenv('ES_HOST', 'http://elasticsearch:9200')}")
    logger.info(f"REDIS_HOST: {os.getenv('REDIS_HOST', 'redis')}")
    logger.info(f"SPEED_LAYER: {os.getenv('ENABLE_SPEED_LAYER', 'false')}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Stock Serving API...")

@app.get("/")
def root():
    return {
        "name": "Stock Serving API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/api/v1/health",
            "docs": "/docs",
            "ohlcv_latest": "/api/v1/ohlcv/latest/{symbol}",
            "ohlcv_historical": "/api/v1/ohlcv/historical/{symbol}",
            "indicators": "/api/v1/indicators/{symbol}",
            "predictions": "/api/v1/predictions/{symbol}",
            "market_latest": "/api/v1/market/latest/{index_code}",
            "market_compare": "/api/v1/market/compare?indices=VNINDEX,VN30"
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")