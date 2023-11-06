from flask import Flask, request, jsonify
import pika

app = Flask(__name__)

# RabbitMQ setup parameters
credentials = pika.PlainCredentials('guest', 'guest')
connection_parameters = pika.ConnectionParameters(
    host='localhost',
    port=5673,
    credentials=credentials,
    heartbeat=10
)

@app.route('/subscribe', methods=['POST'])
def subscribe():
    connection = pika.BlockingConnection(connection_parameters)
    channel = connection.channel()

    data = request.json
    username = data.get('username')
    topic = data.get('topic')
    if not username or not topic:
        channel.close()
        connection.close()
        return jsonify({'error': 'Missing username or topic'}), 400

    queue_name = username
    # Declare a durable, non-exclusive queue
    queue = channel.queue_declare(queue=queue_name, durable=True, exclusive=False)
    channel.queue_bind(exchange='routing', queue=queue.method.queue, routing_key=topic)

    channel.close()
    connection.close()
    return jsonify({'status': 'subscribed', 'queue': queue_name, 'topic': topic}), 200

@app.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    connection = pika.BlockingConnection(connection_parameters)
    channel = connection.channel()

    data = request.json
    username = data.get('username')
    topic = data.get('topic')
    if not username or not topic:
        channel.close()
        connection.close()
        return jsonify({'error': 'Missing username or topic'}), 400

    queue_name = username
    #just unbinding not deleting the queue, can be used for other topics
    channel.queue_unbind(exchange='routing', queue=queue_name, routing_key=topic)


    channel.close()
    connection.close()
    return jsonify({'status': 'unsubscribed', 'queue': queue_name, 'topic': topic}), 200

@app.route('/get_message', methods=['GET'])
def get_message():
    connection = pika.BlockingConnection(connection_parameters)
    channel = connection.channel()

    username = request.args.get('username')
    if not username:
        channel.close()
        connection.close()
        return jsonify({'error': 'Missing username parameter'}), 400

    queue_name = username

    try:
        method_frame, header_frame, body = channel.basic_get(queue=queue_name, auto_ack=True)
        if method_frame:
            message = body.decode('utf-8')
            response = jsonify({'status': 'success', 'message': message}), 200
        else:
            response = jsonify({'status': 'empty', 'message': 'No message available'}), 200
    except pika.exceptions.ChannelClosedByBroker as e:
        # case where the queue does not exist
        response = jsonify({'error': str(e)}), 404
    except Exception as e:
        # exceptions
        response = jsonify({'error': 'An error occurred'}), 500
    finally:
        channel.close()
        connection.close()

    return response


if __name__ == '__main__':
    app.run(debug=True)
