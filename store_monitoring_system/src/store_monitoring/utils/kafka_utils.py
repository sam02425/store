from kafka import KafkaProducer, KafkaConsumer
import json

KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092']

class KafkaProducer:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    def send(self, topic, message):
        self.producer.send(topic, message)
        self.producer.flush()

class KafkaConsumer:
    def __init__(self, *topics):
        self.consumer = KafkaConsumer(
            *topics,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )

    def __iter__(self):
        return iter(self.consumer)