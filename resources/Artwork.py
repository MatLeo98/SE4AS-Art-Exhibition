import random
from random import randint
from paho.mqtt.client import Client
import Lamp


class Artwork:
    name = ""
    light = 0

    def __init__(self, name: str, light: int, room: int):
        self.name = name
        self.light = light
        self.room = room
        self.devices = [Lamp.Lamp(self)]

    def simulate(self, client: Client):
        rand = random.randint(0, 9)
        if rand == 0:
            self.light = self.light + randint(-1, 1)

        client.publish(f"artworks/{self.name}/light/value", self.light)
        client.publish(f"artworks/{self.name}/room/value", self.room)

        print(f'Publishing data for {self.name}')
