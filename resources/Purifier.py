from threading import Thread
import paho.mqtt.client as mqtt
from constants import mqtt_url


class Purifier:
    def __init__(self, room):
        self.room = room
        self.power = 50
        self.client = mqtt.Client(client_id=f"Purifier_{room.name}")
        self.client.connect(mqtt_url, 1884)
        self.thread = Thread(target=self.initialize_mqtt)
        self.thread.start()

    def initialize_mqtt(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        self.client.subscribe("purifier/#")

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode("utf-8")
        topic = msg.topic
        topic_split = topic.split('/')
        room_name = topic_split[1]
        condition = topic_split[2]

        if room_name == self.room.name:
            if condition == 'up':
                self.increase_air()
            elif condition == 'down':
                self.decrease_air()
            elif condition == 'max-up':
                self.max_purification()
            elif condition == 'max-down':
                self.min_purification()

    def increase_air(self):
        self.power = self.power + 10

    def decrease_air(self):
        self.power = self.power - 10

    def max_purification(self):
        self.power = 100

    def min_purification(self):
        self.power = 0
