import time
import paho.mqtt.client as mqtt

from Artwork import Artwork
from Room import Room
from ModeDefinition import ModeDefinition


def main():
    # MQTT client creation
    client = mqtt.Client("resources", reconnect_on_failure=True)
    client.connect("localhost", 1884) #works on IDE
    # client.connect("173.20.0.100", port=1884) #works with docker

    # room creation
    rooms = []
    artworks = []

    room1 = Room(name="room1", temperature=22, humidity=50, air=30, people=10, smoke=0)
    rooms.append(room1)
    room2 = Room(name="room2", temperature=20, humidity=52, air=21, people=10, smoke=0)
    rooms.append(room2)
    room3 = Room(name="room3", temperature=22, humidity=35, air=15, people=10, smoke=0)
    rooms.append(room3)
    room4 = Room(name="room4", temperature=27, humidity=51, air=46, people=10, smoke=0)
    rooms.append(room4)

    gioconda = Artwork(name="Gioconda", light=30, room=1)
    artworks.append(gioconda)
    guernica = Artwork(name="Guernica", light=25, room=2)
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
