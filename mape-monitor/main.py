from KnowledgeStore import write
import paho.mqtt.client as mqtt
from constants import mqtt_url

client = mqtt.Client(client_id="mape-monitor", reconnect_on_failure=True)
client.connect(mqtt_url, 1884)
client.on_connect = lambda client, _, __, ___: (
    client.subscribe("rooms/#"),
    client.subscribe("artworks/#")
)
client.on_message = lambda client, _, msg: (
    print(f"{msg.topic}: {msg.payload.decode('utf-8')}"),
    write(msg.topic, msg.payload.decode("utf-8"))
)
client.loop_forever()
