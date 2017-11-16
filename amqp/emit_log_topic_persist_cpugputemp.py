#!/usr/bin/env python

import subprocess
import pika
import sys
import re

if sys.version_info < (3, 0):
    sys.stdout.write("Sorry, requires Python 3.x, not Python 2.x\n")
    sys.exit(1)

# Constantss
sensorCPU = '/sys/class/thermal/thermal_zone0/temp'
sensorGPU = 'vcgencmd measure_temp'

def getcputemp():
    """Returns temperature of the CPU"""
    file = open(sensorCPU, "r")
    temp = float(int(file.readline())/1000)
    file.close()
    return temp

def getgputemp():
    """Returns temperature of the GPU in raw temp=41.9'C"""
    tempraw = subprocess.check_output(sensorGPU.split()).decode('utf-8')
    m = re.search(r'^temp=(\d+)\.(\d+)', tempraw)
    if not m:
        temp = "invalid"
    else:
        temp = float(m.group(1) + '.' + m.group(2))
    return temp

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