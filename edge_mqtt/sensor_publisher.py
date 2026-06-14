import json
import os
import random
import socket
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt


MQTT_HOST = os.environ.get("MQTT_HOST", "mqtt-broker.cloud-course.svc.cluster.local")
MQTT_PORT = int(os.environ.get("MQTT_PORT", "1883"))
TOPIC = os.environ.get("MQTT_TOPIC", "edge/sensor/temperature")
EDGE_NODE = os.environ.get("EDGE_NODE", socket.gethostname())
INTERVAL_SECONDS = float(os.environ.get("INTERVAL_SECONDS", "2"))
MESSAGE_COUNT = int(os.environ.get("MESSAGE_COUNT", "30"))


def build_payload(seq: int) -> str:
    payload = {
        "seq": seq,
        "edge_node": EDGE_NODE,
        "temperature": round(23.0 + random.random() * 8.0, 2),
        "humidity": round(45.0 + random.random() * 20.0, 2),
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    return json.dumps(payload, ensure_ascii=False)


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(MQTT_HOST, MQTT_PORT, keepalive=30)
    client.loop_start()

    for seq in range(1, MESSAGE_COUNT + 1):
        payload = build_payload(seq)
        result = client.publish(TOPIC, payload, qos=1)
        result.wait_for_publish()
        print(f"published topic={TOPIC} payload={payload}", flush=True)
        time.sleep(INTERVAL_SECONDS)

    client.loop_stop()
    client.disconnect()


if __name__ == "__main__":
    main()
