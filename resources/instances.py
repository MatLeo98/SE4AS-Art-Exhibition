from Artwork import Artwork
from Room import Room


def instances_definition():

    rooms = []
    artworks = []

    # Rooms
    room1 = Room(name="room1", temperature=22, humidity=50, air=30, people=10, smoke=0, window=False)
    room2 = Room(name="room2", temperature=20, humidity=52, air=21, people=10, smoke=0, window=False)
    room3 = Room(name="room3", temperature=22, humidity=35, air=15, people=10, smoke=0, window=False)
    room4 = Room(name="room4", temperature=27, humidity=51, air=46, people=10, smoke=0, window=False)
    rooms.extend([room1, room2, room3, room4])

    # Artworks
    gioconda = Artwork(name="Gioconda", light=150, room=1)
    guernica = Artwork(name="Guernica", light=120, room=2)
    newyorkcity1 = Artwork(name="NewYorkCity1", light=100, room=3)
    persistenza = Artwork(name="LaPersistenzaDellaMemoria", light=130, room=4)
    artworks.extend([gioconda, guernica, newyorkcity1, persistenza])

    return rooms, artworks
