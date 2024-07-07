import multiprocessing
from services.face_recognition_service import FaceRecognitionService
from services.product_detection_service import ProductDetectionService
from services.customer_tracking_service import CustomerTrackingService
from services.planogram_analysis_service import PlanogramAnalysisService
from services.checkout_verification_service import CheckoutVerificationService
from services.inventory_management_service import InventoryManagementService
from api.main import app
from utils.logging_utils import setup_logger
import logging
import uvicorn

main_logger = setup_logger('main', 'logs/main.log')


def run_face_recognition():
    service = FaceRecognitionService()
    service.run()

def run_product_detection():
    service = ProductDetectionService()
    service.run()

def run_customer_tracking():
    service = CustomerTrackingService()
    service.run()

def run_planogram_analysis():
    service = PlanogramAnalysisService()
    service.run()

def run_checkout_verification():
    service = CheckoutVerificationService()
    service.run()

def run_inventory_management():
    service = InventoryManagementService()
    service.run()

def run_api():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    processes = []
    services = [
        run_face_recognition,
        run_product_detection,
        run_customer_tracking,
        run_planogram_analysis,
        run_checkout_verification,
        run_inventory_management,
        run_api
    ]

    try:
        for service in services:
            process = multiprocessing.Process(target=service)
            processes.append(process)
            process.start()
            main_logger.info(f"Started process for {service.__name__}")

        for process in processes:
            process.join()
    except Exception as e:
        main_logger.error(f"Error in main process: {str(e)}", exc_info=True)
    finally:
        for process in processes:
            process.terminate()
        main_logger.info("All processes terminated")