import cv2
import numpy as np
from ultralytics import YOLO
from ..models.database import CartItem, Product
from ..utils.kafka_utils import KafkaProducer, KafkaConsumer
from ..utils.db_utils import get_db_session
import base64
from ..config import config

class ProductDetectionService:
    def __init__(self):
        self.product_detector = YOLO(config.PRODUCT_DETECTION_MODEL)
        self.kafka_consumer = KafkaConsumer('checkout_video_stream', bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS)
        self.kafka_producer = KafkaProducer(bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS)
        self.db_session = get_db_session()

    def detect_products(self, frame):
        results = self.product_detector(frame)
        detected_products = []

        for result in results:
            boxes = result.boxes.xyxy.cpu().numpy().astype(int)
            classes = result.boxes.cls.cpu().numpy().astype(int)

            for cls in classes:
                detected_products.append(cls)

        return detected_products

    def update_cart(self, customer_id, product_ids):
        for product_id in product_ids:
            cart_item = self.db_session.query(CartItem).filter_by(customer_id=customer_id, product_id=product_id).first()
            if cart_item:
                cart_item.quantity += 1
            else:
                new_item = CartItem(customer_id=customer_id, product_id=product_id, quantity=1)
                self.db_session.add(new_item)
        self.db_session.commit()

    def run(self):
        for message in self.kafka_consumer:
            frame = cv2.imdecode(np.frombuffer(base64.b64decode(message.value['frame']), np.uint8), cv2.IMREAD_COLOR)
            customer_id = message.value.get('customer_id')
            if customer_id:
                products = self.detect_products(frame)
                self.update_cart(customer_id, products)
                self.kafka_producer.send('cart_updated', {'customer_id': customer_id, 'products': products})

if __name__ == "__main__":
    service = ProductDetectionService()
    service.run()