from threading import Thread
import paho.mqtt.client as mqtt
# from tenacity import retry

class Conditioner:

    # @retry()
    def __init__(self, room):
        self.room = room
        self.client = mqtt.Client(client_id=f"Conditioner_{room.name}")
        self.client.connect("173.20.0.100", 1883)
        #self.client.connect("localhost", 1883)
        self.thread = Thread(target=self.initialize_mqtt)
        self.thread.start()

    def initialize_mqtt(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        self.client.subscribe("conditioner/#")


    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode("utf-8")
        topic = msg.topic
        topic_split = topic.split('/')
        room_name = topic_split[1]
        condition = topic_split[2]

        if room_name == self.room.name:
            if condition == 'up':
                self.increaseTemperature()
            else:
                self.decreaseTemperature()
    def increaseTemperature(self):
        self.room.temperature = self.room.temperature + 1

    def decreaseTemperature(self):
        self.room.temperature = self.room.temperature - 1