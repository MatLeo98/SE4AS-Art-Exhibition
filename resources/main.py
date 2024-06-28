import time
import paho.mqtt.client as mqtt

from Artwork import Artwork
from Room import Room
from ModeDefinition import ModeDefinition
from constants import mqtt_url


def main():
    client = mqtt.Client("resources", reconnect_on_failure=True)
    client.connect(mqtt_url, 1884)

    rooms = []
    artworks = []

    room1 = Room(name="room1", temperature=22, humidity=50, air=30, people=10, smoke=0, window=False)
    rooms.append(room1)
    room2 = Room(name="room2", temperature=20, humidity=52, air=21, people=10, smoke=0, window=False)
    rooms.append(room2)
    room3 = Room(name="room3", temperature=22, humidity=35, air=15, people=10, smoke=0, window=False)
    rooms.append(room3)
    room4 = Room(name="room4", temperature=27, humidity=51, air=46, people=10, smoke=0, window=False)
    rooms.append(room4)

    gioconda = Artwork(name="Gioconda", light=150, room=1)
    artworks.append(gioconda)
    guernica = Artwork(name="Guernica", light=120, room=2)
    artworks.append(guernica)

    modes = ModeDefinition()
    modes.storeModes(rooms)

    while True:
        for room in rooms:
            room.simulate(client=client)
        for art in artworks:
            art.simulate(client=client)

        time.sleep(1)


if __name__ == "__main__":
    main()
