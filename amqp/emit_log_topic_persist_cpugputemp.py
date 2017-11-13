#!/usr/bin/env python

import pika
import sys

if sys.version_info < (3, 0):
    sys.stdout.write("Sorry, requires Python 3.x, not Python 2.x\n")
    sys.exit(1)

# Constants
sensorCPU = '/sys/class/thermal/thermal_zone0/temp'
sensorGPU = 'vcgencmd measure_temp'

def getcputemp():
    """Returns temperature of the CPU"""
    file = open(getCPUtempFile, "r")
    temp = float(int(file.readline())/1000)
    file.close()
    return temp

def getgputemp():
    """Returns temperature of the GPU"""
    tempraw = subprocess.check_output(sensorGPU.split()).decode('utf-8')
    return tempraw

print(getcputemp())
print(getgputemp())

sys.exit(0)

connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='topic_logs_persistent',
                         exchange_type='topic',
                         durable=True)

routing_key = sys.argv[1] if len(sys.argv) > 2 else 'anonymous.info'
message = ' '.join(sys.argv[2:]) or 'Hello World!'
channel.basic_publish(exchange='topic_logs_persistent',
                      routing_key=routing_key,
                      body=message,
                      properties=pika.BasicProperties(
                         delivery_mode = 2, # make message persistent
                      ))
print(" [x] Sent %r:%r" % (routing_key, message))
connection.close()