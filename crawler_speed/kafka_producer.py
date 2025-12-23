import json
import logging
from kafka import KafkaProducer
from config import Config

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)
class KafkaHandler:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=Config.KAFKA_BOOTSTRAP.split(","),
            value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
            linger_ms=50,
            retries=3
        )

    def send(self, message: dict):
        self.producer.send(Config.KAFKA_TOPIC, message)

    def flush(self):
        self.producer.flush()

    def close(self):
        self.producer.close()
