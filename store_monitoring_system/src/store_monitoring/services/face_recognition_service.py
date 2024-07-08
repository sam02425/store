import cv2
import numpy as np
from ultralytics import YOLO
from sentence_transformers import SentenceTransformer
from ..models.database import Customer
from ..utils.kafka_utils import KafkaProducer, KafkaConsumer
from ..utils.redis_utils import RedisClient
from ..utils.db_utils import get_db_session
import base64
from ..config import config

class FaceRecognitionService:
    def __init__(self):
        self.face_detector = YOLO(config.FACE_DETECTION_MODEL)
        self.face_recognizer = SentenceTransformer(config.FACE_RECOGNITION_MODEL)
        self.kafka_consumer = KafkaConsumer('store_video_stream', bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS)
        self.kafka_producer = KafkaProducer(bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS)
        self.redis_client = RedisClient(host=config.REDIS_HOST, port=config.REDIS_PORT)
        self.db_session = get_db_session()

    def process_frame(self, frame):
        results = self.face_detector(frame)

        for result in results:
            boxes = result.boxes.xyxy.cpu().numpy().astype(int)

            for box in boxes:
                face = frame[box[1]:box[3], box[0]:box[2]]
                embedding = self.face_recognizer.encode([face])[0]

                customer_id = self.find_customer(embedding)
                if customer_id:
                    return customer_id

        return None

    def find_customer(self, embedding):
        # First, check Redis cache
        cached_customer = self.redis_client.get(str(embedding))
        if cached_customer:
            return cached_customer

        # If not in cache, check database
        customers = self.db_session.query(Customer).all()

        for customer in customers:
            stored_embedding = np.frombuffer(base64.b64decode(customer.face_encoding))
            if np.dot(embedding, stored_embedding) > 0.9:  # Adjust threshold as needed
                # Cache the result
                self.redis_client.set(str(embedding), customer.id, ex=3600)  # Expire after 1 hour
                return customer.id

        return None

    def run(self):
        for message in self.kafka_consumer:
            frame = cv2.imdecode(np.frombuffer(base64.b64decode(message.value['frame']), np.uint8), cv2.IMREAD_COLOR)
            customer_id = self.process_frame(frame)
            if customer_id:
                self.kafka_producer.send('customer_detected', {'customer_id': customer_id, 'camera_id': message.value['camera_id']})

if __name__ == "__main__":
    service = FaceRecognitionService()
    service.run()