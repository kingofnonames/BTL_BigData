# import json
# import logging
# from kafka import KafkaProducer
# from kafka.errors import KafkaError

# class KafkaHandler:
#     def __init__(self, bootstrap_servers: str):
#         self.producer = KafkaProducer(
#             bootstrap_servers=bootstrap_servers,
#             key_serializer=lambda k: k.encode("utf-8"),
#             value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
#             linger_ms=50, 
#             retries=5,
#             acks="all"
#         )

#     def send_event(self, topic: str, key: str, event: dict):
#         try:
#             future = self.producer.send(
#                 topic=topic,
#                 key=key,
#                 value=event
#             )
#             future.add_errback(self._on_send_error)
#         except KafkaError as e:
#             logging.error(f"Kafka send failed: {e}")

#     def _on_send_error(self, exc):
#         logging.error(f"Kafka delivery failed: {exc}")

#     def flush(self):
#         self.producer.flush()

#     def close(self):
#         self.producer.flush()
#         self.producer.close()


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