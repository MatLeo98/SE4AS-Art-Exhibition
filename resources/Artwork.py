import random
from random import randint
from paho.mqtt.client import Client
import Lamp


class Artwork:
    name = ""
    light = 0

    def __init__(self, name: str, light: int, room: str):
        self.name = name
        self.light = light
        self.room = room
        self.sensors = [Lamp.Lamp(self)]

    def simulate(self, client: Client):
        rand = random.randint(0, 9)
        if rand == 0:
            self.light = self.light + randint(-1, 1)

        client.publish(f"artworks/{self.name}/light/value", self.light)

        print(f'Publishing data for {self.name}')
