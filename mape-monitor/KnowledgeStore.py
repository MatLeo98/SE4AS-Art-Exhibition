import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS


def write(topic: str, value: int):
    org = "univaq"
    bucket = "artexhibition"
    token = "9mUSjSX8n696aQLPFVrHTD4GBaW5wDAhde9tXtlnuy29KQrQidqWA4w1q7shPBwS3myiRNoTGUkm0FPZBQlNnQ=="
    url = "http://localhost:8086/"
    # url = "http://175.20.0.103:8086/"
    client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
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
