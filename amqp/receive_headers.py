#!/usr/bin/env python

# Source: http://deontologician.tumblr.com/post/19741542377/using-pika-to-create-headers-exchanges-with

import pika
import sys

connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='headers_persistent',
                         exchange_type='headers',
                         durable=True)

result = channel.queue_declare(exclusive=True)
if not result:
    print('Queue didnt declare properly!')
    sys.exit(1)
queue_name = result.method.queue


channel.queue_bind(exchange='headers_persistent',
                   queue=queue_name,
                   routing_key='',
                   arguments={'ham': 'good',
                              'spam': 'bad',
                              'x-match':'all'})

def callback(ch, method, properties, body):
    print("{headers}:{body}".format(headers=properties.headers,
                                    body=body))

channel.basic_consume(callback,
                      queue=queue_name,
                      no_ack=True)

try:
    channel.start_consuming()
except KeyboardInterrupt:
    print('Bye')
    connection.close()
    sys.exit(0)

