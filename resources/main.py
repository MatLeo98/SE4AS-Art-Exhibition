import time
import paho.mqtt.client as mqtt
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

from instances import instances_definition
from constants import *

mqtt_client = mqtt.Client("resources", reconnect_on_failure=True)
mqtt_client.connect(mqtt_url, 1884)
influx_client = influxdb_client.InfluxDBClient(url=influx_url, token=token, org=org)

rooms, artworks = instances_definition()

# Rooms' mode initialization to 'normal'
for room in rooms:
    p = influxdb_client.Point("rooms").tag("room", room.name).field("mode", 1)
    influx_client.write_api(write_options=SYNCHRONOUS).write(bucket=bucket, org=org, record=p)

while True:
    for room in rooms:
        room.simulate(client=mqtt_client)
    for art in artworks:
        art.simulate(client=mqtt_client)

    time.sleep(5)
