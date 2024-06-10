import traceback
from datetime import datetime
from time import sleep
import numpy
from tenacity import retry
import KnowledgeRetrieving
import requests


def main():
    try:
        rooms = KnowledgeRetrieving.get_rooms_name()
        measurements = ["humidity", "temperature", "light", "air"]
        parameters_data = {}
        presence_data = {}

        for room in rooms:
            timeSlots = check_busy_time_slot(room)
            for timeSlot in timeSlots.items():
                KnowledgeRetrieving.storeTimeSlots(timeSlot, room)
            presence = check_presence(room)
            if presence != 0:
                presence_data[room] = presence

        # url = 'http://localhost:5007/planner/presence'
        url = 'http://173.20.0.105:5007/planner/presence'
        x = requests.post(url, json=presence_data)

        # dictionary of data are organized in this way {room : {measurement : {time : value}}}
        for room in rooms:
            room_values = {}
            for measurement in measurements:
                # returns {time : value} of the measurement
                value = KnowledgeRetrieving.get_parameters_db(room, measurement) # CAMBIATO IN get_artworks_db
                room_values[measurement] = value

            parameters_data[room] = room_values

        symptoms = check_parameters_symptoms(parameters_data)
        # url = 'http://localhost:5007/planner/symptoms'
        url = 'http://173.20.0.105:5007/planner/symptoms'
        x = requests.post(url, json=symptoms)

    except Exception as exc:
        traceback.print_exc()


# calulate the mean of the last 5 minutes for each measured parameter (except the movement) and finds the symptoms
def check_parameters_symptoms(data):
    rooms = {}
    ranges = KnowledgeRetrieving.getAllRangesForModes()
    for room in data:
        values = {}
        interval = int(KnowledgeRetrieving.getRangeRoom(room=room))
        mode = KnowledgeRetrieving.getModeRoom(room)
        for measurement in data[room]:
            if measurement != "movement":
                target = int(KnowledgeRetrieving.getTargetRoomParameter(measurement=measurement))
                actual_value = numpy.mean(list(data[room][measurement].values()))

                # 2 means to increase the value and set mode to danger
                # 1 means to increase the value
                # 0 don't do anything
                # -1 means to decrease the value
                # -2 means to decrease the value and set mode to danger
                # 3 means to deactivate alarm and set mode to eco

                print(
                    f'\nRoom: {room}, Mode: {mode}, Measurement: {measurement}, Value: {actual_value}, Target: {target}+/-{interval}')
                if mode == 'eco' or mode == 'normal':
                    if actual_value > target + interval:  # se misura è maggiore del range della mode attuale
                        if actual_value < target + int(ranges['danger']):  # se misura è nel range della danger
                            values[measurement] = 1
                            print('Simply decrease')
                        else:
                            if measurement == 'temperature':
                                values[measurement] = 2
                                print('Danger, decrease and set mode to danger')
                            else:
                                values[measurement] = 1
                                print('Simply decrease')
                    elif actual_value < target - interval:  # se misura è minore del range della mode attuale
                        if actual_value > target - int(ranges['danger']):  # se misura è nel range della danger
                            values[measurement] = -1
                            print('Simply increase')
                        else:
                            if measurement == 'temperature':
                                values[measurement] = -2
                                print('Danger, increase and set mode to danger')
                            else:
                                values[measurement] = -1
                                print('Simply increase')
                elif mode == 'danger':
                    if measurement == "temperature":
                        if actual_value > target + int(ranges['danger']):  # se misura è superiore al range della danger
                            print('Danger active, simply decrease')
                            values[measurement] = 1
                        elif actual_value < target - int(
                                ranges['danger']):  # se misura è superiore al range della danger
                            print('Danger active, simply increase')
                            values[measurement] = -1
                        elif actual_value < target + int(ranges['danger']) and actual_value > target - int(
                                ranges['danger']):
                            print('No more danger, deactivate alarm and set mode to eco')
                            values[measurement] = 3
                    else:
                        if actual_value > target + interval:  # se misura è maggiore del range della mode attuale
                            values[measurement] = 1
                            print('Simply decrease')
                        elif actual_value < target - interval:  # se misura è minore del range della mode attuale
                            values[measurement] = -1
                            print('Simply increase')

        rooms[room] = values
    return rooms


@retry()
def check_busy_time_slot(room):
    rooms = KnowledgeRetrieving.get_rooms_name()
    datas = []
    data = KnowledgeRetrieving.getPresenceDataFromDB(room)
    for element in data.items():
        datas.append(element)

    parsed_time = dict()
    for element in datas:
        time_string = element[0].split('T')
        time_string = time_string[1]
        time_string = time_string.split('.')
        time_string = time_string[0]

        date_obj = datetime.strptime(time_string, '%H:%M:%S')
        parsed_time[str(date_obj.time())] = element[1]

    fasce_orarie = dict()
    for hour in range(0, 24):
        for quarter in [('00', '14'), ('15', '29'), ('30', '44'), ('45', '59')]:
            parsed = list()
            for record in parsed_time.items():
                date_obj = datetime.strptime(record[0], '%H:%M:%S')
                if date_obj.hour == hour and (date_obj.minute > int(quarter[0]) and date_obj.minute < int(quarter[1])):
                    parsed.append(record[1])
                else:
                    parsed.append(0)
            mean = numpy.mean(parsed)
            if mean >= 0.5:
                fasce_orarie[f'{hour}:{quarter[0]} - {hour}:{quarter[1]}'] = 1
            else:
                fasce_orarie[f'{hour}:{quarter[0]} - {hour}:{quarter[1]}'] = 0
    return fasce_orarie


def check_presence(room: str):
    mode = KnowledgeRetrieving.getModeRoom(room)
    utcnow = datetime.utcnow()
    current_time = utcnow.strftime("%H:%M").split(":")

    if current_time[0] != "00":
        current_time[0] = str(int(current_time[0]))
    else:
        current_time[0] = "0"

    for quarter in [('00', '14'), ('15', '29'), ('30', '44'), ('45', '59')]:
        if current_time[1] >= quarter[0] and current_time[1] <= quarter[1]:

            # time_slot = f'{current_time[0]}:{quarter[0]} - {current_time[0]}:{quarter[1]}'

            # value = con.get_room_time_slots(room, time_slot)
            value = KnowledgeRetrieving.get_room_presence(room)
            # print(value)

            if mode == 'normal' and value == 0:
                print(f'{room}: set mode to eco')
                return 1
            if mode == 'eco' and value == 1:
                print(f'{room}: set mode to normal')
                return 2

            return 0


if __name__ == "__main__":

    while True:
        main()
        sleep(10)
