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
        self.client.subscribe(f"conditioner/{self.room}/#")

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode("utf-8")
        topic = msg.topic
        topic_split = topic.split('/')
        room_name = topic_split[1]
        condition = topic_split[2]

        if room_name == self.room.name:
            if condition == 'up':
                self.increaseTemperature()
            elif condition == 'down':
                self.decreaseTemperature()
            elif condition == 'max-up':
                self.maxTemperature()
            elif condition == 'max-down':
                self.minTemperature()


    def increaseTemperature(self):
        self.temperature = self.temperature + 1

    def decreaseTemperature(self):
        self.temperature = self.temperature - 1

    def maxTemperature(self):
        self.temperature = 30

    def minTemperature(self):
        self.temperature = 15
