import cv2
import numpy as np
from ultralytics import YOLO
from ..models.database import CartItem, Product
from ..utils.kafka_utils import KafkaProducer, KafkaConsumer
from ..utils.db_utils import get_db_session
import base64

class CheckoutVerificationService:
    def __init__(self):
        self.product_detector = YOLO('yolov8x.pt')  # Using YOLOv8x for high accuracy
        self.kafka_consumer = KafkaConsumer('checkout_video_stream')
        self.kafka_producer = KafkaProducer()
        self.db_session = get_db_session()

    def detect_products(self, frame):
        results = self.product_detector(frame)
        detected_products = []

        for result in results:
            classes = result.boxes.cls.cpu().numpy().astype(int)

            for cls in classes:
                detected_products.append(cls)

        return detected_products

    def get_cart_items(self, customer_id):
        cart_items = self.db_session.query(CartItem).filter_by(customer_id=customer_id).all()
        return {item.product_id: item.quantity for item in cart_items}

    def verify_checkout(self, customer_id, detected_products):
        cart_items = self.get_cart_items(customer_id)
        checkout_products = {}
        for product_id in detected_products:
            checkout_products[product_id] = checkout_products.get(product_id, 0) + 1

        missing_products = {k: v for k, v in cart_items.items() if k not in checkout_products or checkout_products[k] < v}
        extra_products = {k: v for k, v in checkout_products.items() if k not in cart_items or cart_items[k] < v}

        return missing_products, extra_products

    def run(self):
        for message in self.kafka_consumer:
            frame1 = cv2.imdecode(np.frombuffer(base64.b64decode(message.value['frame1']), np.uint8), cv2.IMREAD_COLOR)
            frame2 = cv2.imdecode(np.frombuffer(base64.b64decode(message.value['frame2']), np.uint8), cv2.IMREAD_COLOR)
            customer_id = message.value['customer_id']

            detected_products1 = self.detect_products(frame1)
            detected_products2 = self.detect_products(frame2)

            # Combine detections from both cameras
            all_detected_products = detected_products1 + detected_products2

            missing_products, extra_products = self.verify_checkout(customer_id, all_detected_products)

            if missing_products or extra_products:
                self.kafka_producer.send('checkout_mismatch', {
                    'customer_id': customer_id,
                    'missing_products': missing_products,
                    'extra_products': extra_products
                })
            else:
                self.kafka_producer.send('checkout_verified', {'customer_id': customer_id})

if __name__ == "__main__":
    service = CheckoutVerificationService()
    service.run()