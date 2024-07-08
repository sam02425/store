import unittest
from unittest.mock import MagicMock, patch
from src.store_monitoring.services.checkout_verification_service import CheckoutVerificationService
from src.store_monitoring.models.database import Customer, Product, CartItem

class TestCheckoutProcess(unittest.TestCase):

    def setUp(self):
        self.service = CheckoutVerificationService()

    @patch('src.store_monitoring.services.checkout_verification_service.get_db_session')
    @patch('src.store_monitoring.services.checkout_verification_service.YOLO')
    def test_verify_checkout(self, mock_yolo, mock_get_db_session):
        # Mock the database session
        mock_session = MagicMock()
        mock_get_db_session.return_value = mock_session

        # Mock the product detector
        mock_detector = MagicMock()
        mock_detector.return_value = [MagicMock(
            boxes=MagicMock(cls=MagicMock(cpu=MagicMock(return_value=np.array([1, 2, 3]))))
        )]
        mock_yolo.return_value = mock_detector

        # Set up test data
        customer_id = 1
        mock_session.query.return_value.filter_by.return_value.all.return_value = [
            CartItem(customer_id=customer_id, product_id=1, quantity=2),
            CartItem(customer_id=customer_id, product_id=2, quantity=1),
        ]

        # Mock frames
        frame1 = np.random.rand(200, 200, 3)
        frame2 = np.random.rand(200, 200, 3)

        # Call the method
        missing_products, extra_products = self.service.verify_checkout(customer_id, [frame1, frame2])

        # Assertions
        self.assertEqual(missing_products, {2: 1})  # Product 2 is missing
        self.assertEqual(extra_products, {3: 1})    # Product 3 is extra

    @patch('src.store_monitoring.services.checkout_verification_service.KafkaProducer')
    @patch('src.store_monitoring.services.checkout_verification_service.KafkaConsumer')
    def test_run(self, mock_consumer, mock_producer):
        # Mock Kafka consumer
        mock_consumer.return_value = [
            MagicMock(value={
                'customer_id': 1,
                'frame1': 'base64_encoded_frame1',
                'frame2': 'base64_encoded_frame2'
            })
        ]

        # Mock verify_checkout method
        self.service.verify_checkout = MagicMock(return_value=({}, {}))

        # Mock Kafka producer
        mock_send = MagicMock()
        mock_producer.return_value.send = mock_send

        # Run the service
        self.service.run()

        # Assertions
        self.service.verify_checkout.assert_called_once()
        mock_send.assert_called_once_with('checkout_verified', {'customer_id': 1})

if __name__ == '__main__':
    unittest.main()