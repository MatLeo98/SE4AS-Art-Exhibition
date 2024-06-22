import json
from fastapi import FastAPI
import uvicorn

app = FastAPI()


@app.get("/config/modes/{mode}")
def get_mode(mode: str):
    with open('config.prop', 'r') as c:
        return json.loads(c.read())['mode'].get(mode)


@app.get("/config/modes")
def get_modes():
    with open('config.prop', 'r') as c:
        return json.loads(c.read())['mode']


@app.get("/config/targets/{measurement}")
def get_target(measurement: str):
    with open('config.prop', 'r') as c:
        return json.loads(c.read())['target'].get(measurement)


@app.get("/config/targets")
def get_targets():
    with open('config.prop', 'r') as c:
        return json.loads(c.read())['target']


if __name__ == "__main__":
    uvicorn.run(app, host='localhost', port=5008)
