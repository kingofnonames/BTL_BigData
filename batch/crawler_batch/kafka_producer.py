import json
from kafka import KafkaProducer

class KafkaHandler:
    def __init__(self, bootstrap_servers: str):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8")
        )

    def send(self, topic: str, key: str, payload: dict):
        self.producer.send(topic, key=key, value=payload)

    def close(self):
        self.producer.flush()
        self.producer.close()