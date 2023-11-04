from KnowledgeStore import write
import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, rc):
    client.subscribe("rooms/#")
    client.subscribe("artworks/#")


def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    print(str(msg.topic + ": " + payload))
    write(str(msg.topic), payload)


if __name__ == '__main__':
    client = mqtt.Client(client_id="mape-monitor", reconnect_on_failure=True)
    client.connect("173.20.0.100", 1883)
    client.on_connect = on_connect
    client.on_message = on_message
    client.loop_forever()
