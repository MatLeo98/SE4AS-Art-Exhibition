from fastapi import FastAPI, HTTPException
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import paho.mqtt.client as mqtt
import uvicorn
from ArtExhibition.constants import *

app = FastAPI()
mqtt_client = mqtt.Client("executor")
mqtt_client.connect(mqtt_url, 1884)


@app.post("/mode/{room}/{value}")
async def mode_change(room: str, value: int):
    try:
        client = influxdb_client.InfluxDBClient(url=influx_url, token=token, org=org)
        write_api = client.write_api(write_options=SYNCHRONOUS)
        record = influxdb_client.Point("rooms").tag("room", room).field("mode", value)
        write_api.write(bucket=bucket, org=org, record=record)
        return {"message": "Mode changed successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"{str(e)}, Room not found")


@app.post("/{room}/{measurement}/{value}")
async def apply_tactic(room: str, measurement: str, value: str):
    if measurement == 'temperature':
        mqtt_client.publish(f'conditioner/{room}/{value}')
    elif measurement == 'humidity':
        mqtt_client.publish(f'dehumidifier/{room}/{value}')
    elif measurement == 'air':
        mqtt_client.publish(f'purifier/{room}/{value}')
    elif measurement == 'light':
        mqtt_client.publish(f'shutter/{room}/{value}')

    return {"message": "Tactic applied successfully"}


@app.post("/{room}/smoke-alarm/on")
async def alarm_turn_on(room: str):
    mqtt_client.publish(f'smoke-alarm/{room}/on')
    return {"message": "Alarm turned on successfully"}


@app.post("/{room}/smoke-alarm/off")
async def alarm_turn_off(room: str):
    mqtt_client.publish(f'smoke-alarm/{room}/off')
    return {"message": "Alarm turned off successfully"}


# uvicorn.run(app, host='173.20.0.106', port=5006)
uvicorn.run(app, host='localhost', port=5006)
