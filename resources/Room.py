import random
from random import randint
from paho.mqtt.client import Client
import Conditioner, Dehumidifier, SmokeDetector, SmokeAlarm


class Room:
    name = ""
    temperature = 30

    def __init__(self, name: str, temperature: int):
        self.name = name
        self.temperature = temperature
        self.sensors = [Conditioner.Conditioner(self),
                        Dehumidifier.Dehumidifier(self),
                        SmokeDetector.SmokeDetector(self)]
        self.smokeAlarm = SmokeAlarm.SmokeAlarm()

    def simulate(self, client: Client):
        rand = random.randint(0, 9)
        if rand == 0:
            self.temperature = self.temperature + randint(-1, 1)

        client.publish(f"rooms/{self.name}/temperature", self.temperature)

        print(f'Publishing simulated data for room {self.name}')
