# python 3.6

import random
import time

from paho.mqtt import client as mqtt_client

broker = 'broker.emqx.io'
port = 1883
# topic = "python/mqtt_moje"
# # generate client ID with pub prefix randomly
# client_id = f'python-mqtt-{random.randint(0, 1000)}'
#
# username = 'emqx'
# password = 'public'


def connect_mqtt(username, password, client_id, client=None, userdata=None, flags=None):
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def publish(client, topic, msg):
    result = client.publish(topic, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")


def run(msg, topic, username, password, client_id, client=None, userdata=None, flags=None):
    client = connect_mqtt(username, password, client_id, client, userdata, flags)
    client.loop_start()
    publish(client, topic, msg)


if __name__ == '__main__':
    msg = 'lubie placki'
    # run(msg)
