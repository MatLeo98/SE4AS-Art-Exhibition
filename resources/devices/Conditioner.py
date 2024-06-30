from threading import Thread
import paho.mqtt.client as mqtt
from constants import mqtt_url


class Conditioner:

    def __init__(self, room):
        self.room = room
        self.temperature = 20
        self.client = mqtt.Client(client_id=f"Conditioner_{room.name}")
        self.client.connect(mqtt_url, 1884)
        self.thread = Thread(target=self.initialize_mqtt)
        self.thread.start()

    def initialize_mqtt(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        self.client.subscribe(f"conditioner/{self.room.name}/#")

    def on_message(self, client, userdata, msg):
        topic_split = msg.topic.split('/')
        room_name = topic_split[1]
        action = topic_split[2]

        if room_name == self.room.name:
            if action == 'up':
                self.increase_temperature()
            elif action == 'down':
                self.decrease_temperature()
            elif action == 'max-up':
                self.max_temperature()
            elif action == 'max-down':
                self.min_temperature()

    def increase_temperature(self):
        self.temperature = self.temperature + 1
        print(f"Conditioner temperature for {self.room.name} increased.")

    def decrease_temperature(self):
        self.temperature = self.temperature - 1
        print(f"Conditioner temperature for {self.room.name} decreased.")

    def max_temperature(self):
        self.temperature = 30
        print(f"Conditioner temperature for {self.room.name} set to maximum.")

    def min_temperature(self):
        self.temperature = 15
        print(f"Conditioner temperature for {self.room.name} set to minimum.")
