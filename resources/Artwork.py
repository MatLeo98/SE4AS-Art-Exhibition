import random
from random import randint
from paho.mqtt.client import Client
import Lamp


class Artwork:
    name = ""
    light = 0
    humidity = 0

    def __init__(self, name: str, light: int, humidity: int, room: str):
        self.name = name
        self.light = light
        self.humidity = humidity
        self.room = room
        self.sensors = [Lamp.Lamp(self)]

    def simulate(self, client: Client):
        rand = random.randint(0, 9)
        if rand == 0:
            self.light = self.light + randint(-1, 1)
            self.humidity = self.humidity + randint(-1, 1)

        client.publish(f"artworks/{self.name}/light", self.light)
        client.publish(f"artworks/{self.name}/humidity", self.humidity)

        print(f'Publishing simulated data for artwork {self.name}')
