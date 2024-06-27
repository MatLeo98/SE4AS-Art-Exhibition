import json
from fastapi import FastAPI
import uvicorn

app = FastAPI()


@app.get("/config/danger/{measurement}")
def get_mode(measurement: str):
    with open('config.prop', 'r') as c:
        return json.loads(c.read())['danger'].get(measurement)


@app.get("/config/targets/{measurement}")
def get_target(measurement: str):
    with open('config.prop', 'r') as c:
        return json.loads(c.read())['target'].get(measurement)


@app.get("/config/ranges/{measurement}")
def get_range(measurement: str):
    with open('config.prop', 'r') as c:
        return json.loads(c.read())['range'].get(measurement)


@app.get("/config/targets")
def get_targets():
    with open('config.prop', 'r') as c:
        return json.loads(c.read())['target']


@app.get("/config/illumination")
def get_illumination():
    with open('config.prop', 'r') as c:
        return json.loads(c.read())['illumination']


if __name__ == "__main__":
    uvicorn.run(app, host='localhost', port=5008)
