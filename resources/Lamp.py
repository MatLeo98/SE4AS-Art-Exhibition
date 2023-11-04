from threading import Thread
import paho.mqtt.client as mqtt
from tenacity import retry

class Lamp:

    @retry()
    def __init__(self, artwork):
        self.artwork = artwork
        self.client = mqtt.Client(client_id=f"Lamp_{artwork.artworkName}")
        thread = Thread(target=self.initialize_mqtt)
        thread.start()

    def initialize_mqtt(self):
        #self.client.connect("localhost", 1883)
        self.client.connect("173.20.0.100", 1883)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        self.client.subscribe("lamp/#")

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode("utf-8")
        topic = msg.topic
        topic_split = topic.split('/')
        room_name = topic_split[1]
        condition = topic_split[2]

        if room_name == self.artwork.artworkName:
            if condition == 'up':
                self.increaseLight()
            else:
                self.decreaseLight()

    def increaseLight(self):
        self.artwork.light = self.artwork.light + 1

    def decreaseLight(self):
        self.artwork.light = self.artwork.light - 1