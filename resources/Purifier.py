from threading import Thread
import paho.mqtt.client as mqtt
from constants import mqtt_url


class Purifier:

    def __init__(self, room):
        self.room = room
        self.power = 50
        self.client = mqtt.Client(client_id=f"Purifier_{room.name}")
        self.client.connect(mqtt_url, 1884)
        self.thread = Thread(target=self.mqtt_init)
        self.thread.start()

    def mqtt_init(self):
        self.client.on_connect = lambda _, __, ___, ____: (
            self.client.subscribe(f"purifier/{self.room.name}/#")
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
                    self.increase_air()
                elif action == 'down':
                    self.decrease_air()
                elif action == 'max-up':
                    self.max_purification()
                elif action == 'max-down':
                    self.min_purification()

    def increase_air(self):
        self.power = self.power + 10
        print(f"Purifier power for {self.room.name} increased.")

    def decrease_air(self):
        self.power = self.power - 10
        print(f"Purifier power for {self.room.name} decreased.")

    def max_purification(self):
        self.power = 100
        print(f"Purifier power for {self.room.name} set to maximum.")

    def min_purification(self):
        self.power = 0
        print(f"Purifier power for {self.room.name} set to minimum.")

    def set_mode(self, mode):
        if mode == "0":
            print("Purifier mode set to eco.")
        elif mode == "1":
            print("Purifier mode set to normal.")
        elif mode == "2":
            print("Purifier mode set to power.")
