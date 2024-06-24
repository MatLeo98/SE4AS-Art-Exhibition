from threading import Thread
import paho.mqtt.client as mqtt


class Shutter:
    def __init__(self, room):
        self.room = room
        self.client = mqtt.Client(client_id=f"Shutter_{room.name}")
        self.client.connect("localhost", 1884)
        self.thread = Thread(target=self.initialize_mqtt)
        self.thread.start()

    def initialize_mqtt(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        self.client.subscribe("shutter/#")

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode("utf-8")
        topic = msg.topic
        topic_split = topic.split('/')
        room_name = topic_split[1]
        condition = topic_split[2]

        if room_name == self.room.name:
            if condition == 'up':
                self.shutter_up()
            else:
                self.shutter_down()

    def shutter_up(self):
        self.room.window = True

    def shutter_down(self):
        self.room.window = False
