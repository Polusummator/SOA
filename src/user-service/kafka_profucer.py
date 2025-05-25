from confluent_kafka import Producer
import json
import os

KAFKA_BROKER = 'kafka:9092'

class KafkaProducer:
    def __init__(self):
        self.producer = Producer({
            'bootstrap.servers': KAFKA_BROKER,
            'message.max.bytes': 10000000
        })

    def produce(self, topic, key, value):
        self.producer.produce(
            topic=topic,
            key=key,
            value=json.dumps(value).encode('utf-8')
        )
        self.producer.flush()

kafka_producer = KafkaProducer()