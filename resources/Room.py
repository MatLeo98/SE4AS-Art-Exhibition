import random
from random import randint

from paho.mqtt.client import Client

import Conditioner
import Dehumidifier
import SmokeAlarm
import SmokeDetector


class Room:
    name = ""
    temperature = 0
    humidity = 0
    air = 0

    def __init__(self, name: str, temperature: int, humidity: int, air: int):
        self.name = name
        self.temperature = temperature
        self.humidity = humidity
        self.air = air
        self.sensors = [Conditioner.Conditioner(self),
                        Dehumidifier.Dehumidifier(self),
                        SmokeDetector.SmokeDetector(self)]
        self.smokeAlarm = SmokeAlarm.SmokeAlarm()

    def simulate(self, client: Client):
        rand = random.randint(0, 9)
        #TODO: DA RANDOMIZZARE MEGLIO
        if rand == 0:
            self.temperature = self.temperature + randint(-1, 1)
            self.humidity = self.humidity + randint(-1, 1)
            self.air = self.air + randint(-1, 1)

        client.publish(f"rooms/{self.name}/temperature/value", self.temperature)
        client.publish(f"rooms/{self.name}/humidity/value", self.humidity)
        client.publish(f"rooms/{self.name}/air/value", self.air)

        print(f'Publishing data for {self.name}')
