import cv2
import numpy as np
from ultralytics import YOLO
from ..utils.kafka_utils import KafkaProducer, KafkaConsumer
import base64
from ..config import config

class CustomerTrackingService:
    def __init__(self):
        self.person_detector = YOLO(config.PERSON_DETECTION_MODEL)
        self.tracker = cv2.TrackerKCF_create()
        self.kafka_consumer = KafkaConsumer('store_video_stream', bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS)
        self.kafka_producer = KafkaProducer(bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS)

    def initialize_tracker(self, frame):
        results = self.person_detector(frame)
        if len(results) > 0:
            box = results[0].boxes.xyxy[0].cpu().numpy()
            self.tracker.init(frame, tuple(box))
        return None

    def track_customer(self, frame):
        success, box = self.tracker.update(frame)
        if success:
            return box
        else:
            return self.initialize_tracker(frame)

    def run(self):
        for message in self.kafka_consumer:
            frame = cv2.imdecode(np.frombuffer(base64.b64decode(message.value['frame']), np.uint8), cv2.IMREAD_COLOR)
            box = self.track_customer(frame)
            if box is not None:
                self.kafka_producer.send('customer_tracked', {'camera_id': message.value['camera_id'], 'box': box.tolist()})

if __name__ == "__main__":
    service = CustomerTrackingService()
    service.run()