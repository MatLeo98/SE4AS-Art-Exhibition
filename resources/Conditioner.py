from threading import Thread
import paho.mqtt.client as mqtt
from constants import mqtt_url


class Conditioner:

    def __init__(self, room):
        self.room = room
        self.temperature = 20
        self.client = mqtt.Client(client_id=f"Conditioner_{room.name}")
        self.client.connect(mqtt_url, 1884)
        self.thread = Thread(target=self.mqtt_init)
        self.thread.start()

    def mqtt_init(self):
        self.client.on_connect = lambda _, __, ___, ____: (
            self.client.subscribe(f"conditioner/{self.room.name}/#")
        )
        self.client.on_message = self.on_message
        self.client.loop_forever()

    def on_message(self, client, userdata, msg):
        topic_split = msg.topic.split('/')
        room_name = topic_split[1]
        action = topic_split[2]

        if room_name == self.room.name:
            if action in ["0","1","2"]:
                self.set_mode(action)
            else:
                if action == 'up':
                    self.increase_temperature()
                elif action == 'down':
                    self.decrease_temperature()
                elif action == 'max-up':
                    self.max_temperature()
                elif action == 'max-down':
                    self.min_temperature()

    def increase_temperature(self):
        self.temperature = self.temperature + 1
        print(f"Conditioner temperature for {self.room.name} increased.")

    def decrease_temperature(self):
        self.temperature = self.temperature - 1
        print(f"Conditioner temperature for {self.room.name} decreased.")

    def max_temperature(self):
        self.temperature = 30
        print(f"Conditioner temperature for {self.room.name} set to maximum.")

    def min_temperature(self):
        self.temperature = 15
        print(f"Conditioner temperature for {self.room.name} set to minimum.")

    def set_mode(self, mode):
        if mode == "0":
            print("Conditioner mode set to eco.")
        elif mode == "1":
            print("Conditioner mode set to normal.")
        elif mode == "2":
            print("Conditioner mode set to power.")

