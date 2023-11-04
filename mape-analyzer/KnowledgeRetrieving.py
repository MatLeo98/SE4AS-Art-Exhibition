import influxdb_client
import requests
from influxdb_client.client.write_api import SYNCHRONOUS
import json

# class KnowledgeRetrieving:

# def __init__(self):
org = "univaq"
token = "4qYRM7usBFEuc3Gxd01lC6Gpiohdwv4DWZ39xjhERohSKddjcpVdlDCzP6aCu8oT"
url = "http://173.20.0.102:8086/"
# url = "http://localhost:8086/"
client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)


def get_rooms_name() -> list:
    query = f'import "influxdata/influxdb/schema" schema.tagValues(bucket: "artexhibition", tag: "room")'
    names = client.query_api().query(org=org, query=query)
    rooms = []
    for element in names.to_values():
        rooms.append(list(element)[2])
    return rooms


def get_artworks_name() -> list:
    query = f'import "influxdata/influxdb/schema" schema.tagValues(bucket: "artexhibition", tag: "artwork")'
    names = client.query_api().query(org=org, query=query)
    artworks = []
    for element in names.to_values():
        artworks.append(list(element)[2])
    return artworks


def getParametersDataFromDB(room, measurement):
    query = f'from(bucket: "seas") |> range(start: -5m)  |> filter(fn: (r) => r["_measurement"] == "indoor")  ' \
            f'|> filter(fn: (r) => r["room"] == "{room}")  |> filter(fn: (r) => r["_field"] == "{measurement}")  ' \
            f'|> yield(name: "last")'
    result = client.query_api().query(org=org, query=query)
    values = {}
    for value in json.loads(result.to_json()):
        values[value['_time']] = value['_value']
    return values


def getPresenceDataFromDB(room):
    # influxdb connection
    org = "univaq"
    token = "seasinfluxdbtoken"
    url = "http://173.20.0.102:8086/"
    # url = "http://localhost:8086/"
    client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
    query_api = client.query_api()
    query = f'from(bucket: "seas")  |> range(start: -7d)  ' \
            f'|> filter(fn: (r) => r["_measurement"] == "indoor")  ' \
            f'|> filter(fn: (r) => r["room"] == "{room}")  ' \
            f'|> filter(fn: (r) => r["_field"] == "movement")  |> yield(name: "mean")'
    result = query_api.query(org=org, query=query)
    values = {}
    for value in json.loads(result.to_json()):
        values[value['_time']] = value['_value']
    return values


def getTargetRoomParameter(measurement):
    url = f'http://173.20.0.108:5008/config/targets/{measurement}'
    response = requests.get(url)
    target = response.json()['data']
    return target


def getRangeRoom(room):
    client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
    query_api = client.query_api()
    query = f'from(bucket: "seas")  |> range(start: 2023-01-01T15:00:00Z)  ' \
            f'|> filter(fn: (r) => r["_measurement"] == "indoor")  |> filter(fn: (r) => r["room"] == "{room}")  ' \
            f'|> filter(fn: (r) => r["_field"] == "range")  |> last(column: "_field")  ' \
            f'|> yield(name: "mean")'
    result = query_api.query(org=org, query=query)
    result = json.loads(result.to_json())[0]['_value']
    return result


def getModeRoom(room):
    query = f'from(bucket: "seas") \
            |> range(start: 2023-01-01T15:00:00Z)\
            |> filter(fn: (r) => r["_measurement"] == "indoor")\
            |> filter(fn: (r) => r["room"] == "{room}")\
            |> filter(fn: (r) => r["_field"] == "mode")\
            |> last(column: "_field") \
            |> yield(name: "last")'
    result = client.query_api().query(org=org, query=query)
    parsed_result = json.loads(result.to_json())[0]['_value']
    return parsed_result


def getAllRangesForModes():
    url = 'http://173.20.0.108:5008/config/modes/all'
    mode_file = requests.get(url)
    modes = mode_file.json()['modes']
    return modes

# Da qui in giù forse va tolto, nel nostro caso non serve
def storeTimeSlots(timeSlot: tuple, room: str):
    # influxdb connection
    bucket = "seas"
    org = "univaq"
    token = "seasinfluxdbtoken"
    # url = "http://localhost:8086/"
    url = "http://173.20.0.102:8086/"
    client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
    write_api = client.write_api(write_options=SYNCHRONOUS)
    measurement = "timeSlot"
    tag = room
    field = timeSlot[0]
    value = timeSlot[1]
    # print(f'Field: {field} - Value: {int(value)}')
    p = influxdb_client.Point(measurement).tag('room', tag).field(field, int(value))
    write_api.write(bucket=bucket, org=org, record=p)


def get_room_time_slots(room: str, timeslot: str):
    query_api = client.query_api()
    query = f'from(bucket: "seas")  |> range(start: -1d)  ' \
            f'|> filter(fn: (r) => r["_measurement"] == "timeSlot")  ' \
            f'|> filter(fn: (r) => r["room"] == "{room}")  ' \
            f'|> filter(fn: (r) => r["_field"] == "{timeslot}")  ' \
            f'|> last(column: "_field")  |> yield(name: "mean")'
    result = query_api.query(org=org, query=query)
    parsed = json.loads(result.to_json())
    return parsed[0]['_value']


def get_room_presence(room):
    query = f'from(bucket: "seas") \
                |> range(start: -15m) \
                |> filter(fn: (r) => r["_measurement"] == "indoor") \
                |> filter(fn: (r) => r["_field"] == "movement") \
                |> filter(fn: (r) => r["room"] == "{room}") \
                |> sort(columns: ["_time"], desc: true) \
                |> first()'
    result = client.query_api().query(org=org, query=query)
    parsed = json.loads(result.to_json())
    return parsed[0]['_value']

# if __name__ == '__main__':
#    DB_Connection.getTargetRoomParameter("temperature")
