from flask import Flask, request, jsonify
import pika

app = Flask(__name__)

# RabbitMQ server connection parameters
# RABBITMQ_HOST = 'localhost'
credentials = pika.PlainCredentials('guest', 'guest')
connection_parameters = pika.ConnectionParameters(
    host='localhost',
    port=5673,
    credentials=credentials,
    heartbeat=10
)
EXCHANGE_NAME = 'routing'

def read_events_from_file(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file.readlines()]

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
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='topic')

    if topic == "internal":
        internal_events = read_events_from_file('internal_events.txt')
        for event in internal_events:
            channel.basic_publish(
                exchange=EXCHANGE_NAME,
                routing_key=topic,
                body=event,
                properties=pika.BasicProperties(delivery_mode=2)  # make message persistent
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

if __name__ == "__main__":
    app.run(debug=True)
