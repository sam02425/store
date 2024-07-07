import cv2
import numpy as np
from ultralytics import YOLO
from ..models.database import Planogram, Product
from ..utils.kafka_utils import KafkaProducer, KafkaConsumer
from ..utils.db_utils import get_db_session
import base64

class PlanogramAnalysisService:
    def __init__(self):
        self.product_detector = YOLO('yolov8x.pt')  # Using YOLOv8x for high accuracy
        self.kafka_consumer = KafkaConsumer('store_video_stream')
        self.kafka_producer = KafkaProducer()
        self.db_session = get_db_session()

    def analyze_planogram(self, frame, aisle_id):
        results = self.product_detector(frame)
        detected_products = []

        for result in results:
            boxes = result.boxes.xyxy.cpu().numpy().astype(int)
            classes = result.boxes.cls.cpu().numpy().astype(int)

            for box, cls in zip(boxes, classes):
                detected_products.append((cls, box[0], box[1]))  # product_id, x, y

        expected_planogram = self.db_session.query(Planogram).filter_by(aisle_id=aisle_id).all()

        misplaced_products = []
        for product in detected_products:
            expected_position = next((p for p in expected_planogram if p.product_id == product[0]), None)
            if expected_position is None or abs(expected_position.position_x - product[1]) > 50 or abs(expected_position.position_y - product[2]) > 50:
                misplaced_products.append(product)

        return misplaced_products

    def run(self):
        for message in self.kafka_consumer:
            frame = cv2.imdecode(np.frombuffer(base64.b64decode(message.value['frame']), np.uint8), cv2.IMREAD_COLOR)
            aisle_id = message.value['aisle_id']
            misplaced_products = self.analyze_planogram(frame, aisle_id)
            if misplaced_products:
                self.kafka_producer.send('planogram_mismatch', {'aisle_id': aisle_id, 'misplaced_products': misplaced_products})

if __name__ == "__main__":
    service = PlanogramAnalysisService()
    service.run()