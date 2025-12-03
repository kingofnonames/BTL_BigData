import faust
import redis.asyncio as redis
from typing import Dict, Any

from config import (
    KAFKA_BROKERS,
    STOCK_TICKER_TOPIC,
    REDIS_HOST,
    REDIS_PORT,
    FAUST_APP_NAME,
    FAUST_WEB_PORT
)
from models import StockTicker

app = faust.App(
    FAUST_APP_NAME,
    broker=f'kafka://{KAFKA_BROKERS[0]}',  
    value_serializer='json',
    web_port=FAUST_WEB_PORT,
    store='memory://', 
)

redis_client: redis.Redis = None

@app.on_started()
async def on_started() -> None:
    """
    Hàm được gọi khi Faust app khởi động, dùng để khởi tạo kết nối Redis.
    """
    global redis_client
    print(f"[{FAUST_APP_NAME}] Connecting to Redis at {REDIS_HOST}:{REDIS_PORT}...")
    try:
        redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        await redis_client.ping()
        print(f"[{FAUST_APP_NAME}] Redis connection successful.")
    except Exception as e:
        print(f"[{FAUST_APP_NAME}] Error connecting to Redis: {e}")

@app.on_stop()
async def on_stop() -> None:
    """
    Hàm được gọi khi Faust app dừng, dùng để đóng kết nối Redis.
    """
    if redis_client:
        await redis_client.close()
        print(f"[{FAUST_APP_NAME}] Redis connection closed.")

ticker_topic = app.topic(
    STOCK_TICKER_TOPIC,
    value_type=StockTicker,  
)


@app.agent(ticker_topic)
async def process_ticker_stream(stream: faust.Stream[StockTicker]) -> None:
    """
    Agent này xử lý từng bản ghi StockTicker:
    1. Nhận dữ liệu đã được xác thực bởi Pydantic (StockTicker).
    2. Cập nhật Giá Cuối cùng (Latest Price) vào Redis.
    """
    global redis_client
    if not redis_client:
        print("Redis client not initialized. Skipping processing.")
        return

    async for ticker in stream:

        
        symbol = ticker.symbol
    
        redis_key_latest_price = f'stock:{symbol}:latest_price'
        data_to_store = {
            'price': str(ticker.price),
            'timestamp': str(ticker.timestamp)
        }
        
        try:
            await redis_client.hset(redis_key_latest_price, mapping=data_to_store)
            
            await redis_client.sadd('monitored_stocks', symbol)

            print(f"[{symbol}] Updated latest price: {ticker.price}. Timestamp: {ticker.timestamp}")
            
        except Exception as e:
            
            print(f"Error writing to Redis for {symbol}: {e}")

if __name__ == '__main__':
    app.main()