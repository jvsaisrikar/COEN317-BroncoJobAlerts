import pika
from pika.exchange_type import ExchangeType

credentials = pika.PlainCredentials('guest', 'guest')
connection_parameters = pika.ConnectionParameters('localhost', port=5673, credentials=credentials)

connection = pika.BlockingConnection(connection_parameters)

channel = connection.channel()

channel.exchange_declare(exchange='routing', exchange_type=ExchangeType.direct)

message = 'This message needs to be routed'


channel.basic_publish(exchange='routing', routing_key='internal', body="message from internal topic")
channel.basic_publish(exchange='routing', routing_key='external', body="message from extenal topic")
channel.basic_publish(exchange='routing', routing_key='both', body="Both internal and external should get this message")


print(f'sent message: {message}')

connection.close()