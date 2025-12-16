from kafka import KafkaProducer
import json

class KafkaHandler:
    def __init__(self, bootstrap_servers='kafka-service:9092'):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    def send(self, topic, df):
        for _, row in df.iterrows():
            self.producer.send(topic, row.to_dict())
        self.producer.flush()
        print(f"✓ Sent {len(df)} records to topic {topic}")