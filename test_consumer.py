import unittest
from unittest.mock import patch, MagicMock
import consumer

class TestConsumerApp(unittest.TestCase):

    def setUp(self):
        self.app = consumer.app.test_client()
        self.app.testing = True

    # Mock the message_consumer function
    @patch('consumer.message_consumer')
    @patch('consumer.pika.BlockingConnection')
    def test_subscribe_success(self, mock_connection, mock_message_consumer):
        mock_channel = MagicMock()
        mock_connection.return_value.channel.return_value = mock_channel

        response = self.app.post('/subscribe', json={
            'username': 'testuser',
            'topic': 'internal'  # Allowed topic
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('subscribed', response.json['status'])

    # Mock the message_consumer function
    @patch('consumer.message_consumer')
    @patch('consumer.pika.BlockingConnection')
    def test_unsubscribe_success(self, mock_connection, mock_message_consumer):
        mock_channel = MagicMock()
        mock_connection.return_value.channel.return_value = mock_channel

        response = self.app.post('/unsubscribe', json={
            'username': 'testuser',
            'topic': 'internal'  # Allowed topic
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('unsubscribed', response.json['status'])

    # Mock the message_consumer function
    @patch('consumer.message_consumer')
    @patch('consumer.fetch_queues')
    def test_start_consumers_on_startup(self, mock_fetch_queues, mock_message_consumer):
        mock_fetch_queues.return_value = ['queue1', 'queue2']
        consumer.start_consumers_on_startup()
        mock_message_consumer.assert_has_calls([
            unittest.mock.call('queue1'),
            unittest.mock.call('queue2')
        ], any_order=True)

if __name__ == '__main__':
    unittest.main()
