#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# COPYRIGHT
#     Copyright (c) 2016 by Cisco Systems, Inc.
#     All rights reserved.
# 
# DESCRIPTION
#    This is a AMQP client side message consumer programme.

from secret import *
import pika
import time
import sys
import ssl
import argparse
import datetime
import logging
import json
from influxdb import InfluxDBClient



def timenownano():
    return "%18.f" % (time.time() * 10 ** 9)


def setupdb(influxDbHost, influxDbPort, influxDbUser, influxDbPassword, influxDbName):

    print("Connect to DB: %s %i" % (influxDbHost, influxDbPort))
    client = InfluxDBClient(influxDbHost, influxDbPort, influxDbUser, influxDbPassword, influxDbName)

    print("Create database: " + influxDbName)
    client.create_database(influxDbName)

    print("Create a retention policy")
    client.create_retention_policy('365d_policy', '365d', 365, default=True)

    print("Switch user: " + influxDbName)
    client.switch_user(influxDbName, influxDbPassword)

    return client


def insertindb(client,line):

    print("Write points: {0}".format(line))
    client.write_points(line, time_precision='ms', protocol='line')

    return True


def callback(ch, method, properties, body):
    print(" [x] rk: {}, headers: {}, msg: {}, ts: {}".
          format(method.routing_key, properties.headers, body,
                 datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")))

    print('-----------')
    dict = json.loads(str(body, 'utf-8'))
    payload = "WaterTemperature,gateway=gw-zh-delft01,units=" + dict['assetpi']['units'] + " " +\
              "average=" + str(dict['assetpi']['temperature']) + " " +\
              str(dict['assetpi']['timestamp'])
    insertindb(main.influxDbClient, payload)

    json_payload = [
        {
            "measurement": "WaterTemperature",
            "tags": {
                "gateway": "gw-zh-delft01",
                "units": dict['assetpi']['units']
            },
            "time": "2009-11-10T23:00:00Z",
            "fields": {
                "average": dict['assetpi']['temperature']
            }
        }
    ]
    print(json_payload)
    # Send to InfluxDB


def main():
    logging.basicConfig(level=logging.INFO)
    
    parser = argparse.ArgumentParser(description="AMQP client")
    parser.add_argument('--version', action='version', version='1.0')
    args = parser.parse_args()
    
    queue_name = user + ':' + datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    credentials = pika.PlainCredentials(user, password)

    main.influxDbClient = setupdb(influxDbHost, influxDbPort, influxDbUser, influxDbPassword, influxDbName)

    try:
        # Setup our ssl options
        ssl_options = ({"ca_certs": "cert.crt",
                       "cert_reqs": ssl.CERT_REQUIRED})
        parameters = pika.ConnectionParameters(
                     host=amqphost, virtual_host=vhost,
                     ssl=True, ssl_options=ssl_options, credentials = credentials, port=port)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, passive=False, 
                              durable=False, exclusive=False, auto_delete=True)
        if label:
            lbl = label.split('=')
            channel.queue_bind(exchange=exchange, queue=queue_name, routing_key=routingkey,
                            arguments = {lbl[0]:lbl[1], 'x-match':'all'})
                            #arguments = {'gatewayId': '9999148', 'x-match':'any'})
        else:
            channel.queue_bind(exchange=exchange, queue=queue_name, routing_key=routingkey)
    except IndexError:
        logging.error("label format error, should be < x=y >!")
        sys.exit()
    except Exception as e:
        logging.error(amqphost + " Connection error!")
        logging.error(" %s", e.message)
        logging.error(type(e))
        sys.exit()
    print(' [*] Waiting for data [tags: {}]. To exit press CTRL+C'.format(label))
    channel.basic_consume(callback,  queue=queue_name, no_ack=True)
    channel.start_consuming()

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == "__main__":
   main()
