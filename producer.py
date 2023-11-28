from flask import Flask, request, jsonify
from pika.exchange_type import ExchangeType
import requests
import pika
import json
import logging

app = Flask(__name__)

credentials = pika.PlainCredentials('guest', 'guest')
connection_parameters = pika.ConnectionParameters(
    host='localhost',
    port=5673,
    credentials=credentials,
    heartbeat=10
)
EXCHANGE_NAME = 'routing'
BROADCAST_TOPIC = 'broadcast'
# Allowed topics
ALLOWED_TOPICS = ['internal', 'external']

def fetch_external_data():
    url = "https://boards-api.greenhouse.io/v1/boards/discord/jobs/"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to fetch data"}


@app.route('/publish', methods=['POST'])
def publish():
    # Get message and topic from POST data
    data = request.json
    message = data.get("message", "")
    topic = data.get("topic", "")
    events = data.get("events", [])

    # Check if the topic is neither 'internal' nor 'external'
    if topic not in ALLOWED_TOPICS:
        error_message = f"Invalid topic specified: {topic}"
        logging.error(error_message)
        return jsonify(status="error", message="Invalid topic specified"), 400

    # Create a connection to the RabbitMQ server
    connection = pika.BlockingConnection(connection_parameters)
    channel = connection.channel()

    # Exchange Declaration
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type=ExchangeType.direct, durable=True)

    if topic == "internal":
        # make message persistent delivery_mode=2
        for event in events:  # Process events from the request
            channel.basic_publish(
                exchange=EXCHANGE_NAME,
                routing_key=topic,
                body=event,
                properties=pika.BasicProperties(delivery_mode=2)  # make message persistent
            )
    elif topic == "external":
        external_data = fetch_external_data()
        if isinstance(external_data, dict) and "error" not in external_data:
            # Converting the dictionary of external events to a JSON-formatted string
            json_data = json.dumps(external_data).encode('utf-8')
            channel.basic_publish(
                exchange=EXCHANGE_NAME,
                routing_key=topic,
                body=json_data,
                properties=pika.BasicProperties(delivery_mode=2)
            )

    connection.close()

    return jsonify(status="success", message="Message(s) published successfully!")


@app.route('/broadcast', methods=['POST'])
def broadcast():
    data = request.json
    urgent_message = data.get("message", "")

    connection = pika.BlockingConnection(connection_parameters)
    channel = connection.channel()

    channel.basic_publish(
        exchange=EXCHANGE_NAME,
        routing_key=BROADCAST_TOPIC,
        body=urgent_message,
        properties=pika.BasicProperties(delivery_mode=2)
    )

    connection.close()

    return jsonify(status="success", message="Broadcast message sent successfully!")


if __name__ == "__main__":
    app.run(debug=True)
