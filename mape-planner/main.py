import requests
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import Dict
import uvicorn
from constants import executor_url

app = FastAPI()


class SymptomsRequest(BaseModel):
    symptoms: Dict[str, Dict[str, int]]


codes = {
    'over': 1,
    'under': -1,
    'over_emergency': 2,
    'under_emergency': -2,
    'deactivate_alarm': 3,
    'activate_alarm': -3
}


@app.post("/planner/symptoms")
async def check_symptoms(request: SymptomsRequest):
    symptoms = request.symptoms

    try:
        for room, measurements in symptoms.items():
            for measurement, condition in measurements.items():
                print(f'\nRoom: {room}, Measurement: {measurement}, Condition: {condition}')
                new_url = f'{executor_url}/{room}/{measurement}'

                if condition == codes['over']:
                    action_url = f'{new_url}/down'
                    action_message = f'{measurement} symptom: {condition}. {measurement} should decrease.'

                elif condition == codes['under']:
                    action_url = f'{new_url}/up'
                    action_message = f'{measurement} symptom: {condition}. {measurement} should increase.'

                elif condition == codes['over_emergency']:
                    action_url = f'{new_url}/max-down'
                    action_message = f'{measurement} symptom: {condition}. {measurement} has a critical value, emergency decrease.'

                elif condition == codes['under_emergency']:
                    action_url = f'{new_url}/max-up'
                    action_message = f'{measurement} symptom: {condition}. {measurement} has a critical value, emergency increase.'

                elif condition in codes['activate_alarm']:
                    action_url = f'{executor_url}/{room}/smoke-alarm/on'
                    action_message = (f'{measurement} symptom: {condition}. '
                                      f'{measurement} should {"decrease" if condition == codes["over_danger"] else "increase"}. '
                                      'Alarm should be activated.')

                elif condition == codes['deactivate_alarm']:
                    action_url = f'{executor_url}/{room}/smoke-alarm/off'
                    action_message = f'{measurement} symptom: {condition}. Alarm should be deactivated.'

                else:
                    continue

                try:
                    requests.get(action_url)
                    print(action_message)
                except requests.RequestException as e:
                    print(f"Request failed for {action_url}: {e}")
                    raise HTTPException(status_code=500, detail=f"Request failed for {action_url}: {e}")

    except Exception as exc:
        print(exc)
        raise HTTPException(status_code=500, detail=str(exc))

    return {"success": True, "error": "none"}


@app.post("/planner/people")
async def change_mode(request: Request):
    modes = await request.json()
    print("New modes: ", modes)

    try:
        for room in modes:
            requests.post(f'{executor_url}/mode/{room}/{modes[room]}')

    except Exception as exc:
        print(exc)
        raise HTTPException(status_code=500, detail=str(exc))

    return {"message": "New modes sent to the executor"}


@app.post("/planner/illumination/{action}")
async def illumination(action: str):
    requests.post(f'{executor_url}/illumination/{action}')


# uvicorn.run(app, host="173.20.0.105", port=5007)
uvicorn.run(app, host="localhost", port=5007)
