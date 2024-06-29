import json
from fastapi import FastAPI
import uvicorn

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


if __name__ == "__main__":
    uvicorn.run(app, host='localhost', port=5008)
