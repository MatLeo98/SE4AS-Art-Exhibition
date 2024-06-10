from KnowledgeStore import write
import paho.mqtt.client as mqtt


def broker_subscription(client, userdata, flags, rc):
    client.subscribe("rooms/#")
    client.subscribe("artworks/#")


def message_received(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    print(msg.topic + ": " + payload)
    write(msg.topic, payload)


if __name__ == '__main__':
    client = mqtt.Client(client_id="mape-monitor", reconnect_on_failure=True)
    client.connect("localhost", 1884)
    client.on_connect = broker_subscription
    client.on_message = message_received
    client.loop_forever()
