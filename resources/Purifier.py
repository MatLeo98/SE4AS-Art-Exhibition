from threading import Thread
import paho.mqtt.client as mqtt
from ArtExhibition.constants import mqtt_url


class Purifier:
    def __init__(self, room):
        self.room = room
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
            else:
                self.decrease_air()

    def increase_air(self):
        self.room.air = self.room.air + 1

    def decrease_air(self):
        self.room.air = self.room.air - 1
