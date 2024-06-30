from threading import Thread
import paho.mqtt.client as mqtt
from constants import mqtt_url


class SmokeDetector:

    def __init__(self, room):
        self.room = room
        self.client = mqtt.Client(client_id=f"SmokeDetector_{room.name}")
        self.client.connect(mqtt_url, 1884)
        self.alarm = False
        self.thread = Thread(target=self.initialize_mqtt)
        self.thread.start()

    def initialize_mqtt(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        self.client.subscribe(f"smoke-alarm/{self.room.name}/#")

    def on_message(self, client, userdata, msg):
        topic_split = msg.topic.split('/')
        condition = topic_split[2]

        if condition == "on":
            self.alarm = True
            print(f"Smoke alarm for {self.room.name} turned on.")
        elif condition == "off":
            self.alarm = False
            print(f"Smoke alarm for {self.room.name} turned off.")
