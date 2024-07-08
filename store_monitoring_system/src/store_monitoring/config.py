import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/store_monitoring")

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092").split(",")

    # Redis
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

    # API
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # Models
    FACE_DETECTION_MODEL = os.getenv("FACE_DETECTION_MODEL", "src/store_monitoring/models/yolov8n-face.pt")
    PRODUCT_DETECTION_MODEL = os.getenv("PRODUCT_DETECTION_MODEL", "src/store_monitoring/models/yolov8x.pt")
    PERSON_DETECTION_MODEL = os.getenv("PERSON_DETECTION_MODEL", "src/store_monitoring/models/yolov8n.pt")
    FACE_RECOGNITION_MODEL = os.getenv("FACE_RECOGNITION_MODEL", "clip-ViT-B-32")

config = Config()