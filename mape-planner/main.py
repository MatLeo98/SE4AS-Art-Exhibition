import requests
from fastapi import FastAPI, Request, HTTPException
import uvicorn
from constants import executor_url, actions

app = FastAPI()


@app.post("/planner/symptoms")
async def check_symptoms(request: Request):
    symptoms = await request.json()

    for room, measurements in symptoms.items():
        for measurement, action in measurements.items():
            print(f'\nRoom: {room}, Measurement: {measurement}, Action: {action}')

            if action in actions:
                action, message = actions[action]
                if action == -3:
                    action_url = f'{executor_url}/{room}/smoke-alarm/on'
                    action_message = message.format(measurement=measurement)
                elif action == 3:
                    action_url = f'{executor_url}/{room}/smoke-alarm/off'
                    action_message = message.format(measurement=measurement)
                else:
                    action_url = f'{executor_url}/{room}/{measurement}/{action}'
                    action_message = message.format(measurement=measurement)

                try:
                    requests.get(action_url)
                    print(action_message)
                except Exception as e:
                    raise HTTPException(status_code=500, detail=str(e))

    return {"message": "Actions sent to the executor"}


@app.post("/planner/people")
async def change_mode(request: Request):
    modes = await request.json()
    print("New modes: ", modes)

    try:
        for room in modes:
            requests.post(f'{executor_url}/mode/{room}/{modes[room]}')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": "New modes sent to the executor"}


@app.post("/planner/illumination/{action}")
async def illumination(action: str):
    requests.post(f'{executor_url}/illumination/{action}')


# uvicorn.run(app, host="173.20.0.105", port=5007)
uvicorn.run(app, host="localhost", port=5007)
