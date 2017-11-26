#!/usr/bin/env python

import sys
if sys.version_info < (3, 0):
    sys.stdout.write("Sorry, requires Python 3.x, not Python 2.x\n")
    sys.exit(1)

import subprocess
import re
import time

# Dependencies
# sudo -H pip3 install paho-mqtt

# Constantss
sensorCPU = '/sys/class/thermal/thermal_zone0/temp'
sensorGPU = 'vcgencmd measure_temp'
mqttHost = 'mo4.bocuse.nl'

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


def publishtemperatures(topic, payload):
    """Publish temperature of MQQT"""

    auth = {'username': "guest", 'password': "guest"}

    publish.single(topic, payload=payload, qos=1, retain=True, hostname=mqttHost,
       port=1883, client_id=None, keepalive=60, will=None, auth=auth, tls=None,
       protocol=mqtt.MQTTv311, transport="tcp")

def main():

    #print(getcputemp())
    #print(getgputemp())

    print("tijd: %18.f" % (time.time()*10**9))

    #h2o_feet,location=coyote_creek water_level=8.120, level\ description = "between 6 and 9 feet" 1439856000
    #weather,location=us-midwest temperature=82 1465839830100400200
    #observations,host="gw1.bocuse.nl" CPUtemperature=18.1,GPUtemperature=11.1 1465839830100400200

    #payload =
    print(time.time() * 10 ** 9)

    #send over MQTT
    #try:
    #    publishtemperatures(topic="", payload="")

    sys.exit(0)


if __name__ == '__main__':
    main()

