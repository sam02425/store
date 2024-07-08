import logging
from logging.handlers import RotatingFileHandler
import os
from ..config import config

def setup_logger(name, log_file, level=config.LOG_LEVEL):
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

    handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

# Setup loggers for each service
face_recognition_logger = setup_logger('face_recognition', 'logs/face_recognition.log')
product_detection_logger = setup_logger('product_detection', 'logs/product_detection.log')
customer_tracking_logger = setup_logger('customer_tracking', 'logs/customer_tracking.log')
planogram_analysis_logger = setup_logger('planogram_analysis', 'logs/planogram_analysis.log')
checkout_verification_logger = setup_logger('checkout_verification', 'logs/checkout_verification.log')
inventory_management_logger = setup_logger('inventory_management', 'logs/inventory_management.log')
api_logger = setup_logger('api', 'logs/api.log')
error_logger = setup_logger('error_handler', 'logs/errors.log')