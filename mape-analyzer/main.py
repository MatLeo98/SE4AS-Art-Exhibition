import traceback
from datetime import datetime, timedelta
from time import sleep
import numpy
from tenacity import retry
import KnowledgeRetrieving
import requests


def main():
    try:
        rooms = KnowledgeRetrieving.get_rooms_name()

        rooms_measurements = ["humidity", "temperature", "air"]

        parameters_data = {}
        presence_data = {}

        for room in rooms:
            timeSlots = check_busy_time_slot(room)
            for timeSlot in timeSlots.items():
                KnowledgeRetrieving.storeTimeSlots(timeSlot, room)
            people = check_people(room)

            presence_data[room] = people
        print("presence_Data:")
        print(presence_data)

        # url = 'http://localhost:5007/planner/presence'
        # url = 'http://173.20.0.105:5007/planner/presence'
        # x = requests.post(url, json=presence_data)

        # dictionary of data are organized in this way {room : {measurement : {time : value}}}
        for room in rooms:
            room_values = {}
            for measurement in rooms_measurements:
                # returns {time : value} of the measurement
                value = KnowledgeRetrieving.get_room_current(room, measurement)
                room_values[measurement] = value

            parameters_data[room] = room_values

        print("parameters_data:")
        print(parameters_data)

        symptoms = check_parameters_symptoms(parameters_data)
        print("symptoms:")
        print(symptoms)
        # url = 'http://localhost:5007/planner/symptoms'
        # url = 'http://173.20.0.105:5007/planner/symptoms'
        # x = requests.post(url, json=symptoms)

        # artworks = KnowledgeRetrieving.get_artworks_name()
        # artworks_measurement = "light"
        # light_data = {}
        #
        # for artwork in artworks:
        #     artwork_values = {}
        #
        #     # returns {time : value} of the measurement
        #     value = KnowledgeRetrieving.get_artwork_current_light(artwork)
        #     artwork_values["light"] = value
        #
        #     light_data[artwork] = artwork_values
        #
        # artwork_symptoms = check_parameters_symptoms(light_data)
        # # url = 'http://localhost:5007/planner/symptoms'
        # url = 'http://173.20.0.105:5007/planner/symptoms'
        # x = requests.post(url, json=symptoms)


    except Exception as exc:
        traceback.print_exc()


# calulate the mean of the last 5 minutes for each measured parameter (except the movement) and finds the symptoms
def check_parameters_symptoms(data):
    rooms = {}
    ranges = KnowledgeRetrieving.get_all_modes_ranges()
    for room in data:
        values = {}
        interval = int(KnowledgeRetrieving.get_range(room=room))
        mode = KnowledgeRetrieving.get_room_mode(room)
        for measurement in data[room]:
            if measurement != "people":
                target = int(KnowledgeRetrieving.get_target_parameter(measurement=measurement))
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

# def check_artwork_symptoms(data):
#     artworks = {}
#     ranges = KnowledgeRetrieving.get_all_modes_ranges()
#     for room in data:
#         values = {}
#         interval = int(KnowledgeRetrieving.get_artwork_light_range(artwork=artwork))
#         mode = KnowledgeRetrieving.get_room_mode(room)
#         for light in data[room]:
#                 target = int(KnowledgeRetrieving.get_target_parameter(measurement"light"))
#                 actual_value = numpy.mean(list(data[room]["light"].values()))
#
#                 # 2 means to increase the value and set mode to danger
#                 # 1 means to increase the value
#                 # 0 don't do anything
#                 # -1 means to decrease the value
#                 # -2 means to decrease the value and set mode to danger
#                 # 3 means to deactivate alarm and set mode to eco
#
#                 print(
#                     f'\nRoom: {room}, Mode: {mode}, Measurement: {measurement}, Value: {actual_value}, Target: {target}+/-{interval}')
#
#                 process_measurement(mode, actual_value, target, interval, ranges, values, measurement)
#
#         rooms[room] = values
#     return rooms

def process_measurement(mode, actual_value, target, interval, ranges, values, measurement):
    def simply_decrease():
        values[measurement] = 1
        print('Simply decrease')

    def simply_increase():
        values[measurement] = -1
        print('Simply increase')

    def danger_decrease():
        values[measurement] = 2
        print('Danger, decrease and set mode to danger')

    def danger_increase():
        values[measurement] = -2
        print('Danger, increase and set mode to danger')

    def no_more_danger():
        values[measurement] = 3
        print('No more danger, deactivate alarm and set mode to eco')

    if mode in ['eco', 'normal']:
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
    elif mode == 'danger':
        if actual_value > target + int(ranges['danger']):
            print('Danger active, simply decrease')
            values[measurement] = 1
        elif actual_value < target - int(ranges['danger']):
            print('Danger active, simply increase')
            values[measurement] = -1
        elif target - int(ranges['danger']) <= actual_value <= target + int(ranges['danger']):
            no_more_danger()


@retry()
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
        if parsed:  # Only calculate the mean if there are records in this time slot
            mean = numpy.mean(parsed)
            if mean >= 10 & mean < 20:
                value = 1  # Normal situation
            elif mean >= 20:
                value = 2  # Overpopulated
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
            return mode

    # Se l'ora corrente non è tra le 8 e le 20, setta ad eco perché il museo è chiuso
    return 0


if __name__ == "__main__":

    while True:
        main()
        sleep(10)
