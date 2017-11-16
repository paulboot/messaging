#!/usr/bin/env python

import subprocess
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


if __name__ == '__main__':

    print(getcputemp())
    print(getgputemp())

    sys.exit(0)
