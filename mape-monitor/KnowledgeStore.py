import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from constants import *


def write(topic: str, value: int):
    client = influxdb_client.InfluxDBClient(url=influx_url, token=token, org=org)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    topic = topic.split("/")
    measurement = topic[0]
    if measurement == 'rooms':
        tag = topic[1]
        field = topic[2]
        p = influxdb_client.Point(measurement).tag("room", tag).field(field, int(value))
    elif measurement == 'artworks':
        tag = topic[1]
        field = topic[2]
        p = influxdb_client.Point(measurement).tag("artwork", tag).field(field, int(value))
    else:
        field = topic[1]
        p = influxdb_client.Point(measurement).field(field, int(value))
    write_api.write(bucket=bucket, org=org, record=p)
