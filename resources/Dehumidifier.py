from threading import Thread
import paho.mqtt.client as mqtt
from constants import mqtt_url


class Dehumidifier:

    def __init__(self, room):
        self.room = room
        self.power = 50
        self.client = mqtt.Client(client_id=f"Dehumidifier_{room.name}")
        thread = Thread(target=self.mqtt_init)
        thread.start()

    def mqtt_init(self):
        self.client.connect(mqtt_url, 1884)
        self.client.on_connect = lambda _, __, ___, ____: (
            self.client.subscribe(f"dehumidifier/{self.room.name}/#")
        )
        self.client.on_message = self.on_message
        self.client.loop_forever()

    def on_message(self, client, userdata, msg):
        topic_split = msg.topic.split('/')
        room_name = topic_split[1]
        action = topic_split[2]

        if room_name == self.room.name:
            if action in ["0","1","2"]:
                self.set_mode(action)
            else:
                if action == 'up':
                    self.increase_humidity()
                elif action == 'down':
                    self.decrease_humidity()
                elif action == 'max-up':
                    self.max_humidity()
                elif action == 'max-down':
                    self.min_humidity()

    def increase_humidity(self):
        self.power = self.power + 10
        print(f"Dehumidifier power for {self.room.name} increased.")

    def decrease_humidity(self):
        self.power = self.power - 10
        print(f"Dehumidifier power for {self.room.name} decreased.")

    def max_humidity(self):
        self.power = 100
        print(f"Dehumidifier power for {self.room.name} set to maximum.")

    def min_humidity(self):
        self.power = 0
        print(f"Dehumidifier power for {self.room.name} set to minimum.")

    def set_mode(self, mode):
        if mode == "0":
            print("Dehumidifier mode set to eco.")
        elif mode == "1":
            print("Dehumidifier mode set to normal.")
        elif mode == "2":
            print("Dehumidifier mode set to power.")