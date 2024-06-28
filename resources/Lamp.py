from threading import Thread
import paho.mqtt.client as mqtt
from constants import mqtt_url

class Lamp:

    def __init__(self, artwork):
        self.artwork = artwork
        self.switch = 0
        self.client = mqtt.Client(client_id=f"Lamp_{artwork.name}")
        thread = Thread(target=self.initialize_mqtt)
        thread.start()

    def initialize_mqtt(self):
        self.client.connect(mqtt_url, 1884)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        self.client.subscribe("illumination/#")

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode("utf-8")
        topic = msg.topic
        topic_split = topic.split('/')
        room_name = topic_split[1]
        condition = topic_split[2]

        if room_name == self.artwork.name:
            if condition == 'on':
                self.turnOn()
            else:
                self.turnOff()

    def turnOn(self):
        self.switch = 1

    def turnOff(self):
        self.switch = 0