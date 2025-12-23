import os
from datetime import datetime, timedelta, timezone

class Config:
    SYMBOLS = os.getenv("SYMBOLS", "FPT,VNM,VCB").split(",")

    DATA_SOURCE = os.getenv("DATA_SOURCE", "VCI")

    START_DATE = os.getenv(
        "START_DATE",
        (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
    )
    END_DATE = os.getenv(
        "END_DATE",
        datetime.now(timezone.utc).strftime("%Y-%m-%d")
    )
    INTERVALS = os.getenv("INTERVALS", "1D").split(",")

    KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")

    TOPIC_OHLCV_RAW = os.getenv("KAFKA_TOPIC_BATCH_OHLCV", "stock.ohlcv.raw")
    TOPIC_FUNDAMENTAL_RAW = os.getenv("TOPIC_FUNDAMENTAL_RAW", "stock.fundamental.raw")
    TOPIC_MARKET_RAW = os.getenv("KAFKA_TOPIC_BATCH_MARKET", "stock.market.raw")

    REQUEST_DELAY = int(os.getenv("REQUEST_DELAY", 1))

    MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
    RETRY_DELAY = int(os.getenv("RETRY_DELAY", 5))
