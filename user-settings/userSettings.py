import json
from fastapi import FastAPI
import uvicorn
from constants import settings_url, parse_url

app = FastAPI()


@app.get("/settings/{room}/danger/{measurement}")
def get_mode(room: str, measurement: str):
    with open('userSettings.prop', 'r') as c:
        return json.loads(c.read())['rooms'][room]['danger'].get(measurement)


@app.get("/settings/{room}/targets/{measurement}")
def get_target(room: str, measurement: str):
    with open('userSettings.prop', 'r') as c:
        return json.loads(c.read())['rooms'][room]['target'].get(measurement)


@app.get("/settings/{room}/ranges/{measurement}")
def get_range(room: str, measurement: str):
    with open('userSettings.prop', 'r') as c:
        return json.loads(c.read())['rooms'][room]['range'].get(measurement)

@app.get("/settings/{artwork}/light/danger")
def get_artwork_danger_light(artwork: str):
    with open('userSettings.prop', 'r') as c:
        return json.loads(c.read())['artworks_light']['danger'].get(artwork)


@app.get("/settings/{artwork}/light/target")
def get_artwork_target_light(artwork: str):
    with open('userSettings.prop', 'r') as c:
        return json.loads(c.read())['artworks_light']['target'].get(artwork)


@app.get("/settings/{artwork}/light/range")
def get_artwork_range_light(artwork: str):
    with open('userSettings.prop', 'r') as c:
        return json.loads(c.read())['artworks_light']['range'].get(artwork)


@app.get("/settings/illumination")
def get_illumination():
    with open('userSettings.prop', 'r') as c:
        return json.loads(c.read())['illumination']


host, port = parse_url(settings_url)
uvicorn.run(app, host=host, port=port)
