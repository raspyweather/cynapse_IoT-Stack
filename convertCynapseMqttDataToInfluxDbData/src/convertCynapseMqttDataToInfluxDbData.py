#!/usr/bin/env python
import os
import paho.mqtt.client as mqtt
import json
from influxdb import InfluxDBClient
from influxdb import SeriesHelper
import uuid
from datetime import datetime
import dateutil.parser as dp
from influxdb.exceptions import InfluxDBClientError

PROCESS_DATA_LENGTH = 7
influxdbData = []

print('Connect to influx database server {}:{}.'.format(
    os.environ['INFLUX_DATABASE_SERVER'], os.environ['INFLUX_DATABASE_SERVER_PORT']))
influxClient = InfluxDBClient(host=os.environ['INFLUX_DATABASE_SERVER'], port=int(
    os.environ['INFLUX_DATABASE_SERVER_PORT']))
print('Connect to influx database {}.'.format(os.environ['INFLUX_DATABASE']))
influxClient.create_database(os.environ['INFLUX_DATABASE'])
influxClient.switch_database(os.environ['INFLUX_DATABASE'])


def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code " + str(rc))
    client.subscribe("#")


def checkTelemetriesReceived(items):
    for item in items:
        if(item["Key"] == "RmsXAxis"):
            #print("RmsXAxis Index", items.index(item))
            return True, items.index(item)
        else:
            continue
    return False, None


# ToDo: Handle diffrent machines
def on_message(client, userdata, msg):
    global influxdbData
    #print("test: ", msg)
    try:
        payload = (msg.payload.decode("utf-8"))

        # return if message topic ist not "TelemetriesReceived"
        if(msg.topic != "TelemetriesReceived"):
            #print("IGNORED " + msg.topic, datetime.now())
            return

        jsonPaylod = json.loads(payload)
        items = jsonPaylod["Telemetries"]["Items"]

        isProcessDataValid, processDataBeginIndex = checkTelemetriesReceived(items)
        if not isProcessDataValid:
            #print("No process data", datetime.now(), "len(items): ", len(items))
            # print(items)
            return

        # return if telemetries received are not process data
        # if not any(item["Key"] == "RmsXAxis" for item in items):

        if any(item["AssetIdShort"] == "zdBPKuu" for item in items) and any(item["AssetIdShort"] == "x3CaSeX" for item in items):
            print("##### Multiple AssetIdShort in one MQTT Message #####")
            print(items)
            print("-----------------------------------------------------")

        #print(items)
        #influxdbData = []

        for i in range(processDataBeginIndex, len(items), PROCESS_DATA_LENGTH):
            json_body = [
                {
                    "measurement": "cynapse",
                    "tags": {
                        "AssetIdShort": items[i]["AssetIdShort"]},
                    "fields": {
                        items[i]["Key"]: items[i]["Value"],
                        items[i+1]["Key"]: items[i+1]["Value"],
                        items[i+2]["Key"]: items[i+2]["Value"],
                        items[i+3]["Key"]: items[i+3]["Value"],
                        items[i+4]["Key"]: items[i+4]["Value"],
                        items[i+5]["Key"]: items[i+5]["Value"],
                        items[i+6]["Key"]: items[i+6]["Value"]},
                    "time": items[i]["Timestamp"],
                }]

            influxdbData += json_body
            
        if len(influxdbData) >= 100:
            influxClient.write_points(influxdbData)
            influxdbData.clear()
        
    except Exception as e:
        print(e)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

print('Connect to MQTT broker {}:{}.'.format(
    os.environ['MQTT_BROKER'], os.environ['MQTT_BROKER_PORT']))
client.connect(os.environ['MQTT_BROKER'], int(
    os.environ['MQTT_BROKER_PORT']), 60)

try:
    client.loop_forever()
except Exception as e:
    print(e)
