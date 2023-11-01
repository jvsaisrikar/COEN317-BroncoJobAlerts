import pika
from pika.exchange_type import ExchangeType

def on_message_received(ch, method, properties, body):
    print(f'External - received new message: {body}')

credentials = pika.PlainCredentials('guest', 'guest')
connection_parameters = pika.ConnectionParameters('localhost', port=5673, credentials=credentials)

connection = pika.BlockingConnection(connection_parameters)

channel = connection.channel()

channel.exchange_declare(exchange='routing', exchange_type=ExchangeType.direct)

queue = channel.queue_declare(queue='', exclusive=True)

channel.queue_bind(exchange='routing', queue=queue.method.queue, routing_key='external')
channel.queue_bind(exchange='routing', queue=queue.method.queue, routing_key='both')
channel.basic_consume(queue=queue.method.queue, auto_ack=True,
    on_message_callback=on_message_received)

print('External Starting Consuming')

channel.start_consuming()