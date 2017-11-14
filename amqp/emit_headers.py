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

fields = {}
try:
    while True:
        data = raw_input('> ')
        if '=' in data:
            key, val = data.split('=')
            fields[key] = val
            continue
        channel.basic_publish(exchange = 'testing',
                              routing_key = '',
                              body = data,
                              properties = \
                                  pika.BasicProperties(headers = fields))
        print(' [x] Send {0} with headers: {1}'.format(data, fields))
except KeyboardInterrupt:
    print('Bye')
    connection.close()
    sys.exit(0)
