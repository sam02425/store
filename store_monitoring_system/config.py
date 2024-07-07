import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/store_monitoring")
    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092").split(",")
    FACE_DETECTION_MODEL = os.getenv("FACE_DETECTION_MODEL", "src/store_monitoring/models/yolov8n-face.pt")
    PRODUCT_DETECTION_MODEL = os.getenv("PRODUCT_DETECTION_MODEL", "src/store_monitoring/models/yolov8x.pt")
    PERSON_DETECTION_MODEL = os.getenv("PERSON_DETECTION_MODEL", "src/store_monitoring/models/yolov8n.pt")
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))

config = Config()