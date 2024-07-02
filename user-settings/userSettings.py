import json
from fastapi import FastAPI
import uvicorn
from constants import settings_url, parse_url

app = FastAPI()


@app.get("/settings/danger/{measurement}")
def get_mode(measurement: str):
    with open('userSettings.prop', 'r') as c:
        return json.loads(c.read())['danger'].get(measurement)


@app.get("/settings/targets/{measurement}")
def get_target(measurement: str):
    with open('userSettings.prop', 'r') as c:
        return json.loads(c.read())['target'].get(measurement)


@app.get("/settings/ranges/{measurement}")
def get_range(measurement: str):
    with open('userSettings.prop', 'r') as c:
        return json.loads(c.read())['range'].get(measurement)


@app.get("/settings/targets")
def get_targets():
    with open('userSettings.prop', 'r') as c:
        return json.loads(c.read())['target']


@app.get("/settings/illumination")
def get_illumination():
    with open('userSettings.prop', 'r') as c:
        return json.loads(c.read())['illumination']


host, port = parse_url(settings_url)
uvicorn.run(app, host=host, port=port)
