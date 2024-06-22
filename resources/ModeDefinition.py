import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from ..constants import *

# from tenacity import *

class ModeDefinition:
    # method that stores the modes inside the knowledge (influxdb)
    # @retry()
    def storeModes(self, rooms: list):
        # influxdb connection
        # url = "http://175.20.0.103:8086/"
        client = influxdb_client.InfluxDBClient(url=influx_url, token=token, org=org)
        write_api = client.write_api(write_options=SYNCHRONOUS)
        # query_api = client.query_api()

        # eco -> 0
        # normal -> 1
        # power -> 2

        # mode assignment to the rooms
        for room in rooms:
            measurement = "rooms"
            tag = room.name
            field = "mode"
            value = 1
            p = influxdb_client.Point(measurement).tag("room", tag).field(field, value)
            write_api.write(bucket=bucket, org=org, record=p)

            field = "range"
            p = influxdb_client.Point(measurement).tag("room", tag).field(field, value)
            write_api.write(bucket=bucket, org=org, record=p)
