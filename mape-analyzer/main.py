import traceback
from datetime import datetime, timedelta
from time import sleep
import numpy
import KnowledgeRetrieving
import requests
from ArtExhibition.constants import planner_url


def main():
    try:
        rooms = KnowledgeRetrieving.get_rooms_name()

        rooms_measurements = ["humidity", "temperature", "air"]

        illumination()

        parameters_data = {}
        presence_data = {}

        for room in rooms:
            timeSlots = check_busy_time_slot(room)
            for timeSlot in timeSlots.items():
                KnowledgeRetrieving.storeTimeSlots(timeSlot, room)
            people = check_people(room)

            presence_data[room] = people
        print("Room modes based on people inside:")
        print(presence_data)

        requests.post(f'{planner_url}/planner/people', json=presence_data)

        # dictionary of data are organized in this way {room : {measurement : {time : value}}}
        for room in rooms:
            room_values = {}
            for measurement in rooms_measurements:
                # returns {time : value} of the measurement
                value = KnowledgeRetrieving.get_room_current(room, measurement)
                room_values[measurement] = value

            parameters_data[room] = room_values

        print("Rooms measurements:")
        print(parameters_data)

        symptoms = check_parameters_symptoms(parameters_data)
        print("symptoms:")
        print(symptoms)
        # url = 'http://localhost:5007/planner/symptoms'
        # url = 'http://173.20.0.105:5007/planner/symptoms'
        # x = requests.post(url, json=symptoms)

        artworks = KnowledgeRetrieving.get_artworks_name()
        # artworks = KnowledgeRetrieving.get_artworks()
        light_data = {}

        for artwork in artworks:
            # artwork_values = {}

            # returns {time : value} of the measurement
            light_value = KnowledgeRetrieving.get_artwork_current_light(artwork)
            # artwork_values["light"] = value

            light_data[artwork] = light_value

        print("Artworks light:")
        print(light_data)

        artwork_symptoms = check_artwork_symptoms(light_data)
        print("artworks symptoms:")
        print(artwork_symptoms)
        # # url = 'http://localhost:5007/planner/symptoms'
        # url = 'http://173.20.0.105:5007/planner/symptoms'
        # x = requests.post(url, json=symptoms)


    except Exception as exc:
        traceback.print_exc()


# calulate the mean of the last 5 minutes for each measured parameter (except the movement) and finds the symptoms
def check_parameters_symptoms(data):
    rooms = {}
    ranges = KnowledgeRetrieving.get_danger_threshold()
    for room in data:
        values = {}
        # interval = int(KnowledgeRetrieving.get_range(room=room))
        mode = KnowledgeRetrieving.get_room_mode(room)
        for measurement in data[room]:
            interval = int(KnowledgeRetrieving.get_tollerable_range(measurement=measurement))
            target = int(KnowledgeRetrieving.get_target_thresholds(measurement=measurement))
            actual_value = data[room][measurement]

            # 2 means to increase the value and set mode to danger
            # 1 means to increase the value
            # 0 don't do anything
            # -1 means to decrease the value
            # -2 means to decrease the value and set mode to danger
            # 3 means to deactivate alarm and set mode to eco

            print(
                f'\nRoom: {room}, Mode: {mode}, Measurement: {measurement}, Value: {actual_value}, Target: {target}+/-{interval}')

            process_measurement(mode, actual_value, target, interval, ranges, values, measurement)

        rooms[room] = values
    return rooms


def process_measurement(mode, actual_value, target, interval, ranges, values, measurement):
    def simply_decrease():
        values[measurement] = -1
        print('Simply decrease')

    def simply_increase():
        values[measurement] = 1
        print('Simply increase')

    def danger_decrease():
        values[measurement] = -2
        print('Danger, decrease and set mode to power')

    def danger_increase():
        values[measurement] = 2
        print('Danger, increase and set mode to power')

    def smoke_alarm_off():
        values[measurement] = 3
        print('No more smoke, deactivate smoke alarm')

    def smoke_alarm_on():
        values[measurement] = -3
        print('Smoke detected, activate smoke alarm!')

    if measurement == "smoke":
        if actual_value == 1:
            smoke_alarm_on()
        else:
            smoke_alarm_off()
    else:
        if mode in [0, 1]:  # eco or normal mode
            if actual_value > target + interval:
                if actual_value < target + int(ranges['danger']):
                    simply_decrease()
                else:
                    danger_decrease()

            elif actual_value < target - interval:
                if actual_value > target - int(ranges['danger']):
                    simply_increase()
                else:
                    danger_increase()
        elif mode == 2:  # power mode
            if actual_value > target + int(ranges['danger']):
                print('Power active, simply decrease')
                simply_decrease()
            elif actual_value < target - int(ranges['danger']):
                print('Power active, simply increase')
                simply_increase()


def check_busy_time_slot(room):
    datas = []
    data = KnowledgeRetrieving.get_people_from_db(room)
    for element in data.items():
        datas.append(element)

    parsed_time = dict()
    for element in datas:
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
        value = 0  # Non affollato
        if parsed:  # Calcola la media solo se ci sono record in questa fascia oraria
            mean = numpy.mean(parsed)
            if 10 <= mean < 20:
                value = 1  # Situazione normale
            elif mean >= 20:
                value = 2  # Molto affollato
        # Overpopulated
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

        time_slot_start = datetime.strptime(f'{current_hour}:00:00', '%H:%M:%S')
        time_slot_end = time_slot_start + timedelta(hours=2)
        time_slot = f'{time_slot_start.strftime("%H:%M")} - {time_slot_end.strftime("%H:%M")}'

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
            return mode

    # Se l'ora corrente non è tra le 8 e le 20, setta ad eco perché il museo è chiuso
    return 0


def check_artwork_symptoms(data):
    artworks = {}
    ranges = KnowledgeRetrieving.get_danger_threshold()
    for artwork in data:
        values = {}
        room = KnowledgeRetrieving.get_artwork_room(artwork)
        interval = int(KnowledgeRetrieving.get_tollerable_range("light"))
        mode = KnowledgeRetrieving.get_room_mode("room" + str(room))
        # for artwork in data:
        target = int(KnowledgeRetrieving.get_target_thresholds("light"))
        actual_value = data[artwork]

        # 2 means to increase the value and set mode to danger
        # 1 means to increase the value
        # 0 don't do anything
        # -1 means to decrease the value
        # -2 means to decrease the value and set mode to danger
        # 3 means to deactivate alarm and set mode to eco

        print(
            f'\nArtwork: {artwork} Room: room{room}, Mode: {mode}, Measurement: light, Value: {actual_value}, Target: {target}+/-{interval}')

        process_measurement(mode, actual_value, target, interval, ranges, values, "light")

        artworks[artwork] = values
    return artworks


def illumination():
    art_illumination = KnowledgeRetrieving.get_illumination_range()
    start = art_illumination.get("start_hour")
    end = art_illumination.get("end_hour")
    current_hour = datetime.now().hour
    if start < current_hour < end:
        requests.post(f'{planner_url}/planner/illumination/on')
    else:
        requests.post(f'{planner_url}/planner/illumination/off')


if __name__ == "__main__":

    while True:
        main()
        sleep(10)
