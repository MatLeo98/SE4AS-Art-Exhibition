from datetime import datetime, timedelta
from time import sleep
import numpy
import KnowledgeRetrieving
import requests
from constants import planner_url, rooms_measurements


def artworks_analysis():
    light_data = {}
    artworks = KnowledgeRetrieving.get_artworks_name()

    for artwork in artworks:
        light_value = KnowledgeRetrieving.get_artwork_current_light(artwork)
        light_data[artwork] = light_value

    print("Artworks light:")
    print(light_data)

    artwork_symptoms = check_artwork_symptoms(light_data)
    print("artworks symptoms:")
    print(artwork_symptoms)
    requests.post(f'{planner_url}/planner/artworks-symptoms', json=artwork_symptoms)


def rooms_analysis():
    parameters_data = {}
    presence_data = {}
    rooms_history_presence = {}
    rooms = KnowledgeRetrieving.get_rooms_name()

    for room in rooms:
        time_slots = check_busy_time_slot(room)
        rooms_history_presence[room] = time_slots
        for time_slot in time_slots.items():
            KnowledgeRetrieving.store_time_slots(time_slot, room)

        people = check_people(room)
        presence_data[room] = people
    print("Room modes based on people inside:")
    print(presence_data)

    payload = {
        "presence_data": presence_data,
        "rooms_history_presence": rooms_history_presence
    }

    requests.post(f'{planner_url}/planner/people', json=payload)

    for room in rooms:
        room_values = {}
        for measurement in rooms_measurements:
            value = KnowledgeRetrieving.get_room_current(room, measurement)
            room_values[measurement] = value

        parameters_data[room] = room_values

    print("Rooms measurements:")
    print(parameters_data)

    rooms_symptoms = check_parameters_symptoms(parameters_data)
    print("rooms symptoms:")
    print(rooms_symptoms)
    requests.post(f'{planner_url}/planner/rooms-symptoms', json=rooms_symptoms)


# calulate the mean of the last 5 minutes for each measured parameter (except the movement) and finds the symptoms
def check_parameters_symptoms(data):
    rooms = {}
    interval = 0
    danger_range = 0
    target = 0
    for room in data:
        values = {}
        mode = KnowledgeRetrieving.get_room_mode(room)
        for measurement in data[room]:
            if measurement != "smoke":
                interval = int(KnowledgeRetrieving.get_tollerable_range(room=room, measurement=measurement))
                danger_range = int(KnowledgeRetrieving.get_danger_threshold(room=room, measurement=measurement))
                target = int(KnowledgeRetrieving.get_target_thresholds(room=room, measurement=measurement))
            actual_value = data[room][measurement]

            if measurement != "smoke":
                print(
                    f'\nRoom: {room}, Mode: {mode}, Measurement: {measurement}, Value: {actual_value}, '
                    f'Target: {target}+/-{interval} Danger range: {danger_range}')
            else:
                print(
                    f'\nRoom: {room}, Mode: {mode}, Measurement: {measurement}, Value: {actual_value}')

            process_measurement(actual_value, target, interval, danger_range, values, measurement)

        rooms[room] = values
    return rooms


def process_measurement(actual_value, target, interval, danger_range, values, measurement):
    def simply_decrease():
        values[measurement] = -1
        print('Simply decrease')

    def simply_increase():
        values[measurement] = 1
        print('Simply increase')

    def danger_decrease():
        values[measurement] = -2
        print('Danger, emergency decrease')

    def danger_increase():
        values[measurement] = 2
        print('Danger, emergency increase')

    def smoke_alarm_off():
        values[measurement] = 3
        print('No smoke, deactivate smoke alarm')

    def smoke_alarm_on():
        values[measurement] = -3
        print('Smoke detected, activate smoke alarm!')

    if measurement == "smoke":
        if actual_value == 1:
            smoke_alarm_on()
        else:
            smoke_alarm_off()
    else:
        if actual_value > target + interval:
            if actual_value < target + danger_range:
                simply_decrease()
            else:
                danger_decrease()

        elif actual_value < target - interval:
            if actual_value > target - danger_range:
                simply_increase()
            else:
                danger_increase()


def check_busy_time_slot(room):
    people = []
    data = KnowledgeRetrieving.get_people_from_db(room)
    for element in data.items():
        people.append(element)

    parsed_time = dict()
    for element in people:
        time_string = element[0].split('T')[1].split('.')[0]
        date_obj = datetime.strptime(time_string, '%H:%M:%S')
        parsed_time[str(date_obj.time())] = element[1]

    fasce_orarie = dict()
    for hour in range(8, 20, 2):
        parsed = []
        start_time = datetime.strptime(f'{hour}:00:00', '%H:%M:%S')
        end_time = start_time + timedelta(hours=2)
        for record in parsed_time.items():
            record_time = datetime.strptime(record[0], '%H:%M:%S')
            if start_time <= record_time < end_time:
                parsed.append(record[1])
        value = 0  # Not crowded
        if parsed:  # Calculate the average only if there are records in this time slot
            mean = numpy.mean(parsed)
            if 10 <= mean < 20:
                value = 1  # Normal situation
            elif mean >= 20:
                value = 2  # Very crowded
        fasce_orarie[f'{start_time.time().strftime("%H:%M")} - {end_time.time().strftime("%H:%M")}'] = value
    return fasce_orarie


def check_people(room: str):
    mode = KnowledgeRetrieving.get_room_mode(room)
    utcnow = datetime.utcnow()
    current_hour = utcnow.hour

    # Check if current hour is between 8:00 - 20:00
    if 8 <= current_hour < 20:
        # Adjust hour to the nearest even number for 2-hour time slots
        if current_hour % 2 != 0:
            current_hour -= 1

        value = KnowledgeRetrieving.get_room_people(room)

        print(f'people in {room}: {value}')

        if value < 10:
            new_mode = 0  # eco
        elif 10 <= value <= 20:
            new_mode = 1  # normal
        else:
            new_mode = 2  # power

        if mode != new_mode:
            if new_mode == 0:
                print(f'{room}: set mode to eco')
            elif new_mode == 1:
                print(f'{room}: set mode to normal')
            elif new_mode == 2:
                print(f'{room}: set mode to power')
            return new_mode
        else:
            print(f'{room}: correct mode already set')
            return -1

    # If the current time is not between 8am and 8pm, set to eco because the museum is closed
    elif mode != 0:
        return 0
    else:
        return -1


def check_artwork_symptoms(data):
    artworks = {}
    for artwork in data:
        values = {}
        room = KnowledgeRetrieving.get_artwork_room(artwork)
        light_danger_range = int(KnowledgeRetrieving.get_artwork_light_danger_threshold(artwork))
        interval = int(KnowledgeRetrieving.get_artwork_light_range(artwork))
        target = int(KnowledgeRetrieving.get_artwork_light_target(artwork))
        actual_value = data[artwork]

        print(
            f'\nArtwork: {artwork} Room: room{room}, Measurement: light, Value: {actual_value}, Target: {target}+/-{interval}, Danger range: {light_danger_range}')

        process_measurement(actual_value, target, interval, light_danger_range, values, "light")

        values['room'] = room
        artworks[artwork] = values

    return artworks


def illumination():
    art_illumination = KnowledgeRetrieving.get_illumination_range()
    start = art_illumination.get("start_hour")
    end = art_illumination.get("end_hour")
    current_hour = datetime.now().strftime("%H:%M")
    if current_hour == start:
        requests.post(f'{planner_url}/planner/illumination/on')
    elif current_hour == end:
        requests.post(f'{planner_url}/planner/illumination/off')


while True:
    rooms_analysis()
    artworks_analysis()
    illumination()
    sleep(10)
