import paho.mqtt.client as mqtt
import json

BROKER = "broker.hivemq.com"
TOPIC = "fog/edge01/sensors"

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print("\nFOG NODE RECEIVED RAW MESSAGE:")
    print(payload)

client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, 1883, 60)

print("Fog node listening...")

client.loop_forever()
