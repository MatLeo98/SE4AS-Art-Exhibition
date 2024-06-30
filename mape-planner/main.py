import requests
from fastapi import FastAPI, Request, HTTPException
import uvicorn
from constants import executor_url, actions

app = FastAPI()


@app.post("/planner/rooms-symptoms")
async def rooms_symptoms(request: Request):
    symptoms = await request.json()
    action_url = ''
    action_message = ''

    for room, measurements in symptoms.items():
        for measurement, code in measurements.items():
            print(f'\nRoom: {room}, Measurement: {measurement}, Action: {code}')

            if code in actions:
                action, message = actions[code]
                if code == -3:
                    action_url = f'{executor_url}/{room}/smoke-alarm/on'
                    action_message = message.format(measurement=measurement)
                elif code == 3:
                    action_url = f'{executor_url}/{room}/smoke-alarm/off'
                    action_message = message.format(measurement=measurement)
                else:
                    if measurement != 'smoke':
                        action_url = f'{executor_url}/{room}/{measurement}/{action}'
                        action_message = message.format(measurement=measurement)

                try:
                    requests.post(action_url)
                    print(action_message)
                except Exception as e:
                    raise HTTPException(status_code=500, detail=str(e))

    return {"message": "Actions sent to the executor"}


@app.post("/planner/artworks-symptoms")
async def artworks_symptoms(request: Request):
    symptoms = await request.json()
    action_url = ''
    action_message = ''

    for artwork, measurements in symptoms.items():
        for measurement, code in measurements.items():
            if measurement == "light":
                print(f'\nArtwork: {artwork}, Measurement: {measurement}, Action: {code}')
                artwork = f'{artwork}'
                if code in actions:
                    action, message = actions[code]
                    action_url = f'{executor_url}/room{measurements["room"]}/{measurement}/{action}'
                    action_message = message.format(measurement=measurement)

                try:
                    requests.post(action_url)
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
