import os

class Config:
    SYMBOLS = os.getenv(
        "SYMBOLS",
        "FPT,VNM,VCB"
    ).split(",")

    DATA_SOURCE = os.getenv("DATA_SOURCE", "VCI")

    INTERVAL_SECONDS = int(os.getenv("INTERVAL_SECONDS", "1"))
    REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "0.05"))
    INTERVALS = os.getenv("INTERVALS", "5m")
    KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
    KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "stock.market.speed.raw")

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    REPLAY_DATE = os.getenv("REPLAY_DATE", "2025-12-19")
