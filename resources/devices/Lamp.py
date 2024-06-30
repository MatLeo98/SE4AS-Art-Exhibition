from threading import Thread
import paho.mqtt.client as mqtt
from constants import mqtt_url


class Lamp:

    def __init__(self, father):
        self.father = father
        self.switch = 0
        self.client = mqtt.Client(client_id=f"Lamp_{father.name}")
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
        topic_split = msg.topic.split('/')
        action = topic_split[1]

        if action == 'on':
            self.turn_on()
        else:
            self.turn_off()

    def turn_on(self):
        self.switch = 1
        print(f"Light on for {self.father.name}\n")

    def turn_off(self):
        self.switch = 0
        print(f"Light off for {self.father.name}\n")
