from threading import Thread
import paho.mqtt.client as mqtt
from constants import mqtt_url


class Shutter:

    def __init__(self, room):
        self.room = room
        self.height = 50
        self.client = mqtt.Client(client_id=f"Shutter_{room.name}")
        self.client.connect(mqtt_url, 1884)
        self.thread = Thread(target=self.mqtt_init)
        self.thread.start()

    def mqtt_init(self):
        self.client.on_connect = lambda _, __, ___, ____: (
            self.client.subscribe(f"shutter/{self.room.name}/#")
        )
        self.client.on_message = self.on_message
        self.client.loop_forever()

    def on_message(self, client, userdata, msg):
        topic_split = msg.topic.split('/')
        action = topic_split[2]

        if action == 'up':
            self.shutter_up()
        elif action == 'down':
            self.shutter_down()
        elif action == 'max-up':
            self.shutter_max_opened()
        elif action == 'max-down':
            self.shutter_min_opened()

    def shutter_up(self):
        self.height = self.height + 10
        print(f"Shutter for {self.room.name} up.")

    def shutter_down(self):
        self.height = self.height - 10
        print(f"Shutter for {self.room.name} down.")

    def shutter_max_opened(self):
        self.height = 100
        print(f"Shutter for {self.room.name} up to the maximum.")

    def shutter_min_opened(self):
        self.height = 0
        print(f"Shutter for {self.room.name} down to the minimum.")
