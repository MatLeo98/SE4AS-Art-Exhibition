import time
import paho.mqtt.client as mqtt

from Artwork import Artwork
from Room import Room


def main():
    # MQTT client creation
    client = mqtt.Client("ManagedResource", reconnect_on_failure=True)
    client.connect("localhost", 1883)
    # client.connect("173.20.0.100", port=1883)

    # room creation
    rooms = []
    artworks = []

    room1 = Room(name="room1", temperature=22)
    rooms.append(room1)
    room2 = Room(name="room2", temperature=20)
    rooms.append(room2)
    room3 = Room(name="room3", temperature=22)
    rooms.append(room3)
    room4 = Room(name="room4", temperature=27)
    rooms.append(room4)

    gioconda = Artwork(name="Gioconda", light=30, humidity=50, room="room1")
    artworks.append(gioconda)
    guernica = Artwork(name="Guernica", light=25, humidity=40, room="room2")
    artworks.append(guernica)

    while True:
        for room in rooms:
            room.simulate(client=client)
        for art in artworks:
            art.simulate(client=client)

        time.sleep(1)


if __name__ == "__main__":
    main()
