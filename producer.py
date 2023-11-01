import pika
from pika.exchange_type import ExchangeType

credentials = pika.PlainCredentials('guest', 'guest')
connection_parameters = pika.ConnectionParameters('localhost', port=5673, credentials=credentials)

connection = pika.BlockingConnection(connection_parameters)
<<<<<<< HEAD
channel = connection.channel()
# make exchange durable
channel.exchange_declare(exchange='routing', exchange_type=ExchangeType.direct, durable=True)
message = 'This message needs to be routed'

# sample hardcoded messages
# mark messages as persistent - by setting delivery_mode property = 2
channel.basic_publish(exchange='routing', routing_key='internal', body="message from internal topic **", properties=pika.BasicProperties(delivery_mode=2))
channel.basic_publish(exchange='routing', routing_key='external', body="message from extenal topic 1 **", properties=pika.BasicProperties(delivery_mode=2))
channel.basic_publish(exchange='routing', routing_key='external', body="message from extenal topic 2 **", properties=pika.BasicProperties(delivery_mode=2))
channel.basic_publish(exchange='routing', routing_key='external', body="message from extenal topic 3 **", properties=pika.BasicProperties(delivery_mode=2))
channel.basic_publish(exchange='routing', routing_key='external', body="message from extenal topic 4 **", properties=pika.BasicProperties(delivery_mode=2))
channel.basic_publish(exchange='routing', routing_key='all', body="Both internal and external should get this message **", properties=pika.BasicProperties(delivery_mode=2))

print(f'sent message: {message}')
=======

channel = connection.channel()

channel.exchange_declare(exchange='routing', exchange_type=ExchangeType.direct)

message = 'This message needs to be routed'

channel.basic_publish(exchange='routing', routing_key='external', body="message from extenal topic")
channel.basic_publish(exchange='routing', routing_key='both', body="Both internal and external should get this message")

print(f'sent message: {message}')

>>>>>>> fce6047 (Initial Commit BoilterPlate)
connection.close()