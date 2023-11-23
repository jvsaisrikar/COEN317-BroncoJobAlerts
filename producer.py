from flask import Flask, request, jsonify
import requests
import pika

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


def read_events_from_file(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file.readlines()]
    
def fetch_external_data():
    url = "https://boards-api.greenhouse.io/v1/boards/discord/jobs/"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()  # Assuming the API returns a JSON response
    else:
        return {"error": "Failed to fetch data"}


@app.route('/publish', methods=['POST'])
def publish():
    # Get message and topic from POST data
    data = request.json
    message = data.get("message", "")
    topic = data.get("topic", "")

    # Create a connection to the RabbitMQ server
    # connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    connection = pika.BlockingConnection(connection_parameters)
    channel = connection.channel()

    # Declare an exchange
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='topic', durable=True)

    if topic == "internal":
        internal_events = read_events_from_file('internal_events.txt')
        for event in internal_events:
            channel.basic_publish(
                exchange=EXCHANGE_NAME,
                routing_key=topic,
                body=event,
                properties=pika.BasicProperties(delivery_mode=2)  # make message persistent
            )
    elif topic == "external":
        external_data = fetch_external_data()
        channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key=topic,
            body=str(external_data),
            properties=pika.BasicProperties(delivery_mode=2)
        )
    else:
        channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key=topic,
            body=message,
            properties=pika.BasicProperties(delivery_mode=2)  # make message persistent
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
