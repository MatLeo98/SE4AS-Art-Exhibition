import requests
from fastapi import FastAPI, Request, HTTPException
import uvicorn
from constants import actions, executor_url, planner_url, parse_url
from datetime import datetime, timedelta

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
    data = await request.json()
    presence_data = data.get("presence_data")
    rooms_history_presence = data.get("rooms_history_presence")
    # print("New modes: ", presence_data)

    now = datetime.now()
    current_time = now.time()
    predicted_mode_set = {}


    for room, history in rooms_history_presence.items():
        predicted_mode_set[room] = 0
        for timeslot, mode in history.items():
            start_str, end_str = timeslot.split(" - ")
            timeslot_start = datetime.strptime(start_str, "%H:%M").time()
            timeslot_end = datetime.strptime(end_str, "%H:%M").time()

            if timeslot_start <= current_time < timeslot_end:
                next_timeslot = get_next_timeslot(timeslot)
                if next_timeslot:
                    next_start_str, _ = next_timeslot.split(" - ")
                    next_timeslot_start = datetime.strptime(next_start_str, "%H:%M").time()
                    if (current_time >= (
                            datetime.combine(now.date(), next_timeslot_start) - timedelta(minutes=30)).time()):
                        next_mode = history.get(next_timeslot)
                        if next_mode is not None and next_mode > mode:
                            try:
                                requests.post(f'{executor_url}/mode/{room}/{next_mode}')
                                predicted_mode_set[room] = 1
                                print(f'{room}: set mode to {next_mode} for next timeslot')

                            except Exception as e:
                                raise HTTPException(status_code=500, detail=str(e))

    #Default behavior, set mode based on people inside
    try:
        for room in presence_data:
            if presence_data[room] != -1 and predicted_mode_set[room] == 0:
                print(f'{room}: set mode to {presence_data[room]}')
                requests.post(f'{executor_url}/mode/{room}/{presence_data[room]}')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": "New modes sent to the executor"}

def get_next_timeslot(timeslot):
    times = [
        "08:00 - 10:00", "10:00 - 12:00", "12:00 - 14:00",
        "14:00 - 16:00", "16:00 - 18:00", "18:00 - 20:00"
    ]
    index = times.index(timeslot)
    return times[index + 1] if index + 1 < len(times) else None



@app.post("/planner/illumination/{action}")
async def illumination(action: str):
    requests.post(f'{executor_url}/illumination/{action}')


host, port = parse_url(planner_url)
uvicorn.run(app, host=host, port=port)

@app.post("/planner/set-modes")
async def change_mode_by_timeslot(request: Request):
    modes = await request.json()
    print("New modes: ", modes)

    try:
        for room in modes:
            if modes[room] != -1:
                requests.post(f'{executor_url}/mode/{room}/{modes[room]}')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": "New modes sent to the executor"}
