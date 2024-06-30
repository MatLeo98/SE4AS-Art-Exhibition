import influxdb_client
import requests
from influxdb_client.client.write_api import SYNCHRONOUS
import json
from constants import *

client = influxdb_client.InfluxDBClient(url=influx_url, token=token, org=org)


def query_executor(query):
    return client.query_api().query(org=org, query=query)


def get_rooms_name():
    query = (f'from(bucket: "{bucket}") |> range(start: -30d) |> filter(fn: (r) => r["_measurement"] == "rooms") |> '
             f'group(columns: ["room"]) |> distinct(column: "_value")')
    r = query_executor(query)

    rooms = []
    for element in r.to_values():
        value = list(element)[4]
        if value is not None and value not in rooms:
            rooms.append(value)
    print("rooms: ", rooms)
    return rooms


def get_artworks_name():
    query = (f'from(bucket: "{bucket}") |> range(start: -30d) |> filter(fn: (r) => r["_measurement"] == '
             '"artworks") |> group(columns: ["artwork"]) |> distinct(column: "_value")')
    art = query_executor(query)

    artworks = []
    for element in art.to_values():
        value = list(element)[4]
        if value is not None and value not in artworks:
            artworks.append(value)
    print("artworks: ", artworks)
    return artworks


def get_artwork_room(artwork):
    query = f'from(bucket: "{bucket}")' \
            f'|> range(start: -30d)' \
            f'|> filter(fn: (r) => r["_measurement"] == "artworks") ' \
            f'|> filter(fn: (r) => r["_field"] == "room") ' \
            f'|> filter(fn: (r) => r["artwork"] == "{artwork}") ' \
            f'|> last() ' \
            f'|> yield(name: "last_value")'
    result = client.query_api().query(org=org, query=query)
    result = json.loads(result.to_json())[0]['_value']
    return result


def get_artwork_current_light(artwork):
    query = f'from(bucket: "{bucket}") |> range(start: -30d) ' \
            f'|> filter(fn: (r) => r["_measurement"] == "artworks")' \
            f'|> filter(fn: (r) => r["artwork"] == "{artwork}") ' \
            f'|> filter(fn: (r) => r["_field"] == "light") ' \
            f'|> last() ' \
            f'|> yield(name: "last_value")'
    result = client.query_api().query(org=org, query=query)

    result = json.loads(result.to_json())[0]['_value']
    return result


def get_room_current(room, field):
    query = f'from(bucket: "{bucket}") ' \
            f'|> range(start: -5m) ' \
            f'|> filter(fn: (r) => r["_measurement"] == "rooms") ' \
            f'|> filter(fn: (r) => r["room"] == "{room}") ' \
            f'|> filter(fn: (r) => r["_field"] == "{field}") ' \
            f'|> last() ' \
            f'|> yield(name: "last_value")'
    result = client.query_api().query(org=org, query=query)
    result = json.loads(result.to_json())[0]['_value']
    return result


def get_people_from_db(room):
    client = influxdb_client.InfluxDBClient(url=influx_url, token=token, org=org)
    query_api = client.query_api()
    query = f'from(bucket: "{bucket}")  |> range(start: -7d)  ' \
            f'|> filter(fn: (r) => r["_measurement"] == "rooms")  ' \
            f'|> filter(fn: (r) => r["room"] == "{room}")  ' \
            f'|> filter(fn: (r) => r["_field"] == "people")  |> yield(name: "mean")'
    result = query_api.query(org=org, query=query)
    values = {}
    for value in json.loads(result.to_json()):
        values[value['_time']] = value['_value']
    return values


def get_target_thresholds(measurement):
    return requests.get(f'{settings_url}/settings/targets/{measurement}').json()


def get_tollerable_range(measurement):
    return requests.get(f'{settings_url}/settings/ranges/{measurement}').json()


def get_illumination_range():
    return requests.get(f'{settings_url}/settings/illumination').json()


def get_room_mode(room):
    query = f'from(bucket: "{bucket}") \
            |> range(start: 2024-01-01T15:00:00Z)\
            |> filter(fn: (r) => r["_measurement"] == "rooms")\
            |> filter(fn: (r) => r["room"] == "{room}")\
            |> filter(fn: (r) => r["_field"] == "mode")\
            |> last(column: "_field") \
            |> yield(name: "last")'
    result = client.query_api().query(org=org, query=query)
    parsed_result = json.loads(result.to_json())[0]['_value']
    return parsed_result


def get_danger_threshold(measurement: str):
    return requests.get(f'{settings_url}/settings/danger/{measurement}').json()


def store_time_slots(time_slot: tuple, room: str):
    client = influxdb_client.InfluxDBClient(url=influx_url, token=token, org=org)
    write_api = client.write_api(write_options=SYNCHRONOUS)
    p = influxdb_client.Point("time_slot").tag('room', room).field(time_slot[0], int(time_slot[1]))
    write_api.write(bucket=bucket, org=org, record=p)


def get_room_people(room):
    query = f'from(bucket: "{bucket}") \
                |> range(start: -5m) \
                |> filter(fn: (r) => r["_measurement"] == "rooms") \
                |> filter(fn: (r) => r["_field"] == "people") \
                |> filter(fn: (r) => r["room"] == "{room}") \
                |> sort(columns: ["_time"], desc: true) \
                |> first()'
    result = client.query_api().query(org=org, query=query)
    parsed = json.loads(result.to_json())
    return parsed[0]['_value']
