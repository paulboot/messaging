#!/usr/bin/env python
import pika
import sys

connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='topic_logs_persistent',
                         exchange_type='topic',
                         durable=True)

queue_name = sys.argv[1]
binding_keys = sys.argv[2:]
if not queue_name or not binding_keys:
    sys.stderr.write("Usage: %s [queue_name] [binding_key]...\n" % sys.argv[0])
    sys.exit(1)

result = channel.queue_declare(queue=queue_name,
                               exclusive=False,
                               durable=True)

if not binding_keys:
    sys.stderr.write("Usage: %s [queue_name] [binding_key]...\n" % sys.argv[0])
    sys.exit(1)

for binding_key in binding_keys:
    channel.queue_bind(exchange='topic_logs_persistent',
                       queue=queue_name,
                       routing_key=binding_key)

print(' [*] Waiting for logs. To exit press CTRL+C')

def callback(ch, method, properties, body):
    print(" [x] %r:%r" % (method.routing_key, body))
    ch.basic_ack(delivery_tag = method.delivery_tag)

channel.basic_consume(callback,
                      queue=queue_name,
                      no_ack=False)

channel.start_consuming()
