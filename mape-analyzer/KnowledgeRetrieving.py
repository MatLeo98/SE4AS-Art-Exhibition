import influxdb_client
import requests
from influxdb_client.client.write_api import SYNCHRONOUS
import json

# class KnowledgeRetrieving:

# def __init__(self):
org = "univaq"
token = "CKrRn0kl4k-bXiL4mhNIQ9TAGrBuB6mjzbypZwLDkxA9qAzaWNgVMfgkVplr4Ys7W-Y9xXpPVSEiBtLeIFuP7Q=="
# url = "http://173.20.0.102:8086/"
url = "http://localhost:8086/"
client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)


def query_executor(query):
    return client.query_api().query(org=org, query=query)


def get_rooms_name():
    query = 'from(bucket: "artexhibition") |> range(start: -30d) |> filter(fn: (r) => r["_measurement"] == "rooms") |> group(columns: ["room"]) |> distinct(column: "_value")'
    r = query_executor(query)

    rooms = []
    for element in r.to_values():
        value = list(element)[4]
        if value is not None and value not in rooms:
            rooms.append(value)
    print("rooms: ", rooms)
    return rooms


def get_artworks_name():
    query = ('from(bucket: "artexhibition") |> range(start: -30d) |> filter(fn: (r) => r["_measurement"] == '
             '"artworks") |> group(columns: ["artwork"]) |> distinct(column: "_value")')
    art = query_executor(query)

    artworks = []
    for element in art.to_values():
        value = list(element)[4]
        if value is not None and value not in artworks:
            artworks.append(value)
    print("artworks: ", artworks)
    return artworks


def get_artwork_mean_light(artwork):
    query = f'from(bucket: "artexhibition") |> range(start: -30d) ' \
            f'|> filter(fn: (r) => r["_measurement"] == "artworks")' \
            f'|> filter(fn: (r) => r["artwork"] == "{artwork}") ' \
            f'|> filter(fn: (r) => r["_field"] == "light") ' \
            f'|> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false) ' \
            f'|> yield(name: "mean")'
    result = client.query_api().query(org=org, query=query)
    result = json.loads(result.to_json())[0]['_value']
    return result


def get_artwork_current_light(artwork):
    query = f'from(bucket: "artexhibition") |> range(start: -30d) ' \
            f'|> filter(fn: (r) => r["_measurement"] == "artworks")' \
            f'|> filter(fn: (r) => r["artwork"] == "{artwork}") ' \
            f'|> filter(fn: (r) => r["_field"] == "light") ' \
            f'|> last() ' \
            f'|> yield(name: "last_value")'
    result = client.query_api().query(org=org, query=query)
    result = json.loads(result.to_json())[0]['_value']
    return result


def get_room_mean(room, field):  # field can be temperature, light, humidity or smoke
    query = f'from(bucket: "artexhibition") ' \
            f'|> range(start: -30d) ' \
            f'|> filter(fn: (r) => r["_measurement"] == "rooms") ' \
            f'|> filter(fn: (r) => r["room"] == "{room}") ' \
            f'|> filter(fn: (r) => r["_field"] == "{field}") ' \
            f'|> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false) ' \
            f'|> yield(name: "mean")'
    result = client.query_api().query(org=org, query=query)
    result = json.loads(result.to_json())[0]['_value']
    return result


def get_room_current(room, field):
    query = f'from(bucket: "artexhibition") ' \
            f'|> range(start: -5m) ' \
            f'|> filter(fn: (r) => r["_measurement"] == "rooms") ' \
            f'|> filter(fn: (r) => r["room"] == "{room}") ' \
            f'|> filter(fn: (r) => r["_field"] == "{field}") ' \
            f'|> last() ' \
            f'|> yield(name: "last_value")'
    result = client.query_api().query(org=org, query=query)
    result = json.loads(result.to_json())[0]['_value']
    return result


# TODO: MANCA LA SMOKE, DA DISCUTERE PERCHè PENSO SIA TRUE FALSE

def get_measurement_for_room(room, measurement):
    query = f'from(bucket: "artexhibition") |> range(start: -5m)  |> filter(fn: (r) => r["_measurement"] == "rooms")  ' \
            f'|> filter(fn: (r) => r["room"] == "{room}")  |> filter(fn: (r) => r["_field"] == "{measurement}")  ' \
            f'|> yield(name: "last")'
    result = client.query_api().query(org=org, query=query)
    values = {}
    for value in json.loads(result.to_json()):
        values[value['_time']] = value['_value']
    return values


def get_people_from_db(room):
    org = "univaq"
    # token = "r5EwDxI9D8RNOIkz-84Ozrucn5azbt8u95aqfhvrBzwzHDtACumjD3Rep5TbT4tTQLHAIMoJ3okTUPG_gpSoXg=="
    # url = "http://173.20.0.102:8086/"
    url = "http://localhost:8086/"
    client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
    query_api = client.query_api()
    query = f'from(bucket: "artexhibition")  |> range(start: -7d)  ' \
            f'|> filter(fn: (r) => r["_measurement"] == "rooms")  ' \
            f'|> filter(fn: (r) => r["room"] == "{room}")  ' \
            f'|> filter(fn: (r) => r["_field"] == "people")  |> yield(name: "mean")'
    result = query_api.query(org=org, query=query)
    values = {}
    for value in json.loads(result.to_json()):
        values[value['_time']] = value['_value']
    return values


def get_target_parameter(measurement):  # METODO PER PRENDERSI DA CONFIG LE SOGLIE IMPOSTATE DALL'UTENTE
    # url = f'http://173.20.0.108:5008/config/targets/{measurement}'
    url = f'http://localhost:5008/config/targets/{measurement}'
    response = requests.get(url)
    target = response.json()['data']
    return target


def get_range(room):
    client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
    query_api = client.query_api()
    query = f'from(bucket: "artexhibition")  |> range(start: 2023-01-01T15:00:00Z)  ' \
            f'|> filter(fn: (r) => r["_measurement"] == "rooms")  |> filter(fn: (r) => r["room"] == "{room}")  ' \
            f'|> filter(fn: (r) => r["_field"] == "range")  |> last(column: "_field")  ' \
            f'|> yield(name: "mean")'
    result = query_api.query(org=org, query=query)
    result = json.loads(result.to_json())[0]['_value']
    return result

def get_artwork_light_range(artwork): #TODO: capire cosa fa, se ritorna la media dei valori o se serve quel range
    client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
    query_api = client.query_api()
    query = f'from(bucket: "artexhibition")  |> range(start: 2023-01-01T15:00:00Z)  ' \
            f'|> filter(fn: (r) => r["_measurement"] == "artworks")  |> filter(fn: (r) => r["artwork"] == "{artwork}")  ' \
            f'|> filter(fn: (r) => r["_field"] == "range")  |> last(column: "_field")  ' \
            f'|> yield(name: "mean")'
    result = query_api.query(org=org, query=query)
    result = json.loads(result.to_json())[0]['_value']
    return result


def get_room_mode(room):
    query = f'from(bucket: "artexhibition") \
            |> range(start: 2024-01-01T15:00:00Z)\
            |> filter(fn: (r) => r["_measurement"] == "rooms")\
            |> filter(fn: (r) => r["room"] == "{room}")\
            |> filter(fn: (r) => r["_field"] == "mode")\
            |> last(column: "_field") \
            |> yield(name: "last")'
    result = client.query_api().query(org=org, query=query)
    parsed_result = json.loads(result.to_json())[0]['_value']
    return parsed_result


def get_all_modes_ranges():
    # url = 'http://173.20.0.108:5008/config/modes/all'
    url = 'http://localhost:5008/config/modes/all'
    mode_file = requests.get(url)
    modes = mode_file.json()['modes']
    return modes


def getRoomTemperatureData(room):
    query_api = client.query_api()
    query = f'from(bucket: "artexhibition")  |> range(start: 2024-01-01T15:00:00Z)  ' \
            f'|> filter(fn: (r) => r["_measurement"] == "rooms")  |> filter(fn: (r) => r["room"] == "{room}")  ' \
            f'|> filter(fn: (r) => r["_field"] == "temperature")  |> last(column: "_field")  ' \
            f'|> yield(name: "mean")'
    result = query_api.query(org=org, query=query)
    result = json.loads(result.to_json())[0]['_value']
    print("result: ", result)
    return result

def storeTimeSlots(timeSlot: tuple, room: str):
    # influxdb connection
    bucket = "artexhibition"
    org = "univaq"
    # token = "r5EwDxI9D8RNOIkz-84Ozrucn5azbt8u95aqfhvrBzwzHDtACumjD3Rep5TbT4tTQLHAIMoJ3okTUPG_gpSoXg=="
    url = "http://localhost:8086/"
    # url = "http://175.20.0.103:8086/"
    client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    measurement = "timeSlot"
    tag = room
    field = timeSlot[0]
    value = timeSlot[1]
    # print(f'Field: {field} - Value: {int(value)}')
    p = influxdb_client.Point(measurement).tag('room', tag).field(field, int(value))
    write_api.write(bucket=bucket, org=org, record=p)

def get_room_people(room):
    #TODO: DA CONTROLLARE QUERY
    query = f'from(bucket: "artexhibition") \
                |> range(start: -5m) \
                |> filter(fn: (r) => r["_measurement"] == "rooms") \
                |> filter(fn: (r) => r["_field"] == "people") \
                |> filter(fn: (r) => r["room"] == "{room}") \
                |> sort(columns: ["_time"], desc: true) \
                |> first()'
    result = client.query_api().query(org=org, query=query)
    parsed = json.loads(result.to_json())
    return parsed[0]['_value']


# Da qui in giù forse va tolto, nel nostro caso non serve



# def get_room_time_slots(room: str, timeslot: str):
#     query_api = client.query_api()
#     query = f'from(bucket: "seas")  |> range(start: -1d)  ' \
#             f'|> filter(fn: (r) => r["_measurement"] == "timeSlot")  ' \
#             f'|> filter(fn: (r) => r["room"] == "{room}")  ' \
#             f'|> filter(fn: (r) => r["_field"] == "{timeslot}")  ' \
#             f'|> last(column: "_field")  |> yield(name: "mean")'
#     result = query_api.query(org=org, query=query)
#     parsed = json.loads(result.to_json())
#     return parsed[0]['_value']


# def get_room_presence(room):
#     query = f'from(bucket: "seas") \
#                 |> range(start: -15m) \
#                 |> filter(fn: (r) => r["_measurement"] == "indoor") \
#                 |> filter(fn: (r) => r["_field"] == "movement") \
#                 |> filter(fn: (r) => r["room"] == "{room}") \
#                 |> sort(columns: ["_time"], desc: true) \
#                 |> first()'
#     result = client.query_api().query(org=org, query=query)
#     parsed = json.loads(result.to_json())
#     return parsed[0]['_value']

if __name__ == '__main__':
    # get_artworks_db('Guernica')
    # get_artworks_name()
    # get_rooms_name()
    getRoomTemperatureData('room1')
