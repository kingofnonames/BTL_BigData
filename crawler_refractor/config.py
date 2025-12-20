import os
from datetime import datetime, timedelta

class Config:
    SYMBOLS = os.getenv("SYMBOLS", "FPT,VNM,VCB").split(",")

    DATA_SOURCE = os.getenv("DATA_SOURCE", "TCBS")

    START_DATE = (datetime.now() - timedelta(days=365 * 3)).strftime("%Y-%m-%d")
    END_DATE = datetime.now().strftime("%Y-%m-%d")

    INTERVALS = ["1D", "1W", "1M"]

    KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")

    TOPIC_OHLCV = "stock_ohlcv"
    TOPIC_FUNDAMENTAL = "stock_fundamental"
    TOPIC_MARKET = "stock_market"