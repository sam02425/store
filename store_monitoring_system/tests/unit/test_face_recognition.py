import unittest
import numpy as np
from unittest.mock import MagicMock, patch
from src.store_monitoring.services.face_recognition_service import FaceRecognitionService

class TestFaceRecognitionService(unittest.TestCase):

    def setUp(self):
        self.service = FaceRecognitionService()

    @patch('src.store_monitoring.services.face_recognition_service.YOLO')
    @patch('src.store_monitoring.services.face_recognition_service.SentenceTransformer')
    def test_process_frame(self, mock_transformer, mock_yolo):
        # Mock the YOLO detector
        mock_detector = MagicMock()
        mock_detector.return_value = [MagicMock(boxes=MagicMock(
            xyxy=MagicMock(cpu=MagicMock(return_value=np.array([[0, 0, 100, 100]])))
        ))]
        mock_yolo.return_value = mock_detector

        # Mock the face recognizer
        mock_recognizer = MagicMock()
        mock_recognizer.encode.return_value = [np.array([1, 2, 3])]
        mock_transformer.return_value = mock_recognizer

        # Mock the frame
        frame = np.random.rand(200, 200, 3)

        # Mock the find_customer method
        self.service.find_customer = MagicMock(return_value=1)

        # Call the method
        result = self.service.process_frame(frame)

        # Assertions
        self.assertEqual(result, 1)
        mock_detector.assert_called_once_with(frame)
        mock_recognizer.encode.assert_called_once()
        self.service.find_customer.assert_called_once()

    def test_find_customer(self):
        # Mock the database session and query
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.all.return_value = [
            MagicMock(id=1, face_encoding='AAECAwQFBgc='),  # Base64 encoded [0, 1, 2, 3, 4, 5, 6, 7]
            MagicMock(id=2, face_encoding='CAkKCwwNDg8='),  # Base64 encoded [8, 9, 10, 11, 12, 13, 14, 15]
        ]

        self.service.db_session = mock_session
        self.service.redis_client = MagicMock()
        self.service.redis_client.get.return_value = None

        # Test case 1: Customer found
        embedding = np.array([0, 1, 2, 3, 4, 5, 6, 7])
        result = self.service.find_customer(embedding)
        self.assertEqual(result, 1)

        # Test case 2: Customer not found
        embedding = np.array([16, 17, 18, 19, 20, 21, 22, 23])
        result = self.service.find_customer(embedding)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()