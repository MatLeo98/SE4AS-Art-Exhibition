from threading import Thread
import paho.mqtt.client as mqtt
from constants import mqtt_url


class SmokeDetector:

    # @retry()
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
        self.client.subscribe("smokeDetector/#")

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode("utf-8")
        topic = msg.topic
        topic_split = topic.split('/')
        room_name = topic_split[1]
        condition = topic_split[2]

        if condition == "danger":
            self.alarm = True
        else:
            self.alarm = False
