from threading import Thread
import paho.mqtt.client as mqtt
from constants import mqtt_url

class Dehumidifier:

    def __init__(self, room):
        self.room = room
        self.power = 50
        self.client = mqtt.Client(client_id=f"Dehumidifier_{room.name}")
        thread = Thread(target=self.initialize_mqtt)
        thread.start()

    def initialize_mqtt(self):
        self.client.connect(mqtt_url, 1884)
        # self.client.connect("173.20.0.100", 1884)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        self.client.subscribe("dehumidifier/#")

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode("utf-8")
        topic = msg.topic
        topic_split = topic.split('/')
        room_name = topic_split[1]
        condition = topic_split[2]

        if room_name == self.room.name:
            if condition == 'up':
                self.increaseHumidity()
            elif condition == 'down':
                self.decreaseHumidity()
            elif condition == 'max-up':
                self.maxHumidity()
            elif condition == 'max-down':
                self.minHumidity()

    def increaseHumidity(self):
        self.power = self.power + 10

    def decreaseHumidity(self):
        self.power = self.power - 10

    def maxHumidity(self):
        self.power = 100

    def minHumidity(self):
        self.power = 0