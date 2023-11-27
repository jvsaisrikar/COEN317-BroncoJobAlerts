import unittest
from unittest.mock import patch, MagicMock
import producer  # Importing your Flask app

class TestFlaskApp(unittest.TestCase):

    def setUp(self):
        self.app = producer.app.test_client()
        self.app.testing = True

    @patch('producer.requests.get')  # Mock the requests.get call
    @patch('producer.pika.BlockingConnection')  # Mock the RabbitMQ connection
    def test_fetch_external_data_success(self, mock_connection, mock_requests_get):
        # Mocking the response from Greenhouse API
        mock_requests_get.return_value = MagicMock(status_code=200, json=lambda: {
    "jobs": [
        {
            "absolute_url": "https://boards.greenhouse.io/discord/jobs/7003727002",
            "data_compliance": [
                {
                    "type": "gdpr",
                    "requires_consent": False,
                    "requires_processing_consent": False,
                    "requires_retention_consent": False,
                    "retention_period": None
                }
            ],
            "education": "education_required",
            "internal_job_id": 5672455002,
            "location": {
                "name": "San Francisco or Remote"
            },
            "metadata": [
                {
                    "id": 15769324002,
                    "name": "Jobs Page Display Department Override",
                    "value": "Internships",
                    "value_type": "short_text"
                },
                {
                    "id": 4105571002,
                    "name": "Tier Level",
                    "value": [
                        "1"
                    ],
                    "value_type": "multi_select"
                }
            ],
            "id": 7003727002,
            "updated_at": "2023-11-21T10:46:55-05:00",
            "requisition_id": "6003-S2-2215-DSE-2",
            "title": "Data Science Intern, Causal Inference"
        }
    ]
})

        # Test /publish endpoint with external topic
        response = self.app.post('/publish', json={
            'message': 'Test message',
            'topic': 'external'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', response.json['status'])

    @patch('producer.pika.BlockingConnection')  # Mock the RabbitMQ connection
    def test_publish_internal_topic_success(self, mock_connection):
        # Test /publish endpoint with internal topic
        response = self.app.post('/publish', json={
            'message': 'Test message',
            'topic': 'internal',
            'events': ['event1', 'event2']
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', response.json['status'])

    @patch('producer.pika.BlockingConnection')
    def test_broadcast_success(self, mock_connection):
        # Test /broadcast endpoint
        response = self.app.post('/broadcast', json={
            'message': 'Urgent broadcast message'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', response.json['status'])

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
