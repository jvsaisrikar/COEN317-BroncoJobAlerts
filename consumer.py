from flask import Flask, request, jsonify
from threading import Thread
from requests.auth import HTTPBasicAuth
from threading import Lock
from datetime import datetime
import pika
import sys
import logging
import time
import requests
import pytz

# Lock declaration
subscribe_lock = Lock()
# broadcast topic
BROADCAST_TOPIC = 'broadcast'
def fetch_queues():
    url = "http://localhost:15673/api/queues"
    response = requests.get(url, auth=HTTPBasicAuth('guest', 'guest'))
    if response.status_code == 200:
        queues = response.json()
        return [q['name'] for q in queues if q['name']]  # Filter out any queues without names
    else:
        logging.error(f"Failed to fetch queues: {response.text}")
        return []

class PSTFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        pst_timezone = pytz.timezone('America/Los_Angeles')
        converted_time = datetime.fromtimestamp(record.created, pst_timezone)
        return converted_time.strftime('%Y-%m-%d %H:%M:%S')

def get_current_time_in_pst():
    pst_timezone = pytz.timezone('America/Los_Angeles')
    return datetime.now(pst_timezone).strftime('%Y-%m-%d %H:%M:%S')

# Checking for '--verbose' argument; info logs will be displayed only if verbose is passed
log_level = logging.INFO if '--verbose' in sys.argv else logging.ERROR

# Configure logging
logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')
for handler in logging.root.handlers:
    handler.setFormatter(PSTFormatter())

app = Flask(__name__)

# RabbitMQ setup parameters
credentials = pika.PlainCredentials('guest', 'guest')
connection_parameters = pika.ConnectionParameters(
    host='localhost',
    port=5673,
    credentials=credentials,
    heartbeat=10
)

# Dictionary to store consumer threads
consumer_threads = {}

def message_consumer(queue_name):
    while True:  # Reconnection loop
        try:
            connection = pika.BlockingConnection(connection_parameters)
            channel = connection.channel()
            channel.basic_qos(prefetch_count=1)
            def callback(ch, method, properties, body):
                message = body.decode()
                current_time = get_current_time_in_pst()
                print(f'{current_time} - Received message for user {queue_name}: {message}')
                ch.basic_ack(delivery_tag=method.delivery_tag)

            channel.basic_consume(queue=queue_name, on_message_callback=callback)
            current_time = get_current_time_in_pst()
            print(f'{current_time} - Consuming messages for user: {queue_name}')
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError as e:
            logging.error(f'Connection was closed, retrying in 5 seconds: {e}')
            time.sleep(5)
        except Exception as e:
            logging.error(f'Unexpected error: {e}, exiting consumer thread for {queue_name}')
            break  # Exit the thread if an unexpected error occurs
        finally:
            if connection.is_open:
                connection.close()
@app.route('/subscribe', methods=['POST'])
def subscribe():
    try:
        data = request.json
        username = data.get('username')
        topic = data.get('topic')
        if not username or not topic:
            return jsonify({'error': 'Missing username or topic'}), 400

        connection = pika.BlockingConnection(connection_parameters)
        channel = connection.channel()

        queue_name = username
        channel.queue_declare(queue=queue_name, durable=True, exclusive=False)
        channel.queue_bind(exchange='routing', queue=queue_name, routing_key=BROADCAST_TOPIC)
        # locking here when binding; unlocking will be done after this execution.
        with subscribe_lock:
            channel.queue_bind(exchange='routing', queue=queue_name, routing_key=topic)

        channel.close()
        connection.close()

        if username not in consumer_threads:
            consumer_thread = Thread(target=message_consumer, args=(username,))
            consumer_threads[username] = consumer_thread
            consumer_thread.start()

        return jsonify({'status': 'subscribed', 'queue': queue_name, 'topic': topic}), 200
    except Exception as e:
        logging.error(f"Subscription error: {e}")
        return jsonify({'error': 'Failed to subscribe', 'details': str(e)}), 500



@app.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    data = request.json
    username = data.get('username')
    topic = data.get('topic')

    if not username or not topic:
        return jsonify({'error': 'Missing username or topic'}), 400

    # Check if the topic is 'broadcast'
    if topic == 'broadcast':
        return jsonify({'error': 'Unsubscribing from the broadcast topic is not allowed'}), 400

    try:
        connection = pika.BlockingConnection(connection_parameters)
        channel = connection.channel()

        # Unbind the topic from the user's queue
        # locking here when unbinding; unlocking will be done after this execution.
        with subscribe_lock:
            channel.queue_unbind(queue=username, exchange='routing', routing_key=topic)

        channel.close()
        connection.close()
        return jsonify({'status': 'unsubscribed', 'queue': username, 'topic': topic,
                        'message': 'Topic unbound from queue successfully'}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to unbind topic from queue', 'details': str(e)}), 500

def start_consumers_on_startup():
    queue_names = fetch_queues()
    for queue_name in queue_names:
        if queue_name not in consumer_threads:
            consumer_thread = Thread(target=message_consumer, args=(queue_name,))
            consumer_threads[queue_name] = consumer_thread
            consumer_thread.start()
            current_time = get_current_time_in_pst()
            print(f"{current_time} - Active User: {queue_name}")

if __name__ == '__main__':
    start_consumers_on_startup()
    app.run(debug=True, port=5001)
