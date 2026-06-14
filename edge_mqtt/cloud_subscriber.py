import json
import os
from datetime import datetime, timezone

import paho.mqtt.client as mqtt
import redis


MQTT_HOST = os.environ.get("MQTT_HOST", "mqtt-broker.cloud-course.svc.cluster.local")
MQTT_PORT = int(os.environ.get("MQTT_PORT", "1883"))
TOPIC = os.environ.get("MQTT_TOPIC", "edge/sensor/#")
REDIS_HOST = os.environ.get("REDIS_HOST", "redis-svc.cloud-course.svc.cluster.local")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", "cloud-course-2026")
REDIS_KEY = os.environ.get("REDIS_KEY", "edge:mqtt:events")


redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD or None,
    decode_responses=True,
)


def on_connect(client, userdata, flags, reason_code, properties):
    print(f"connected to mqtt reason_code={reason_code}", flush=True)
    client.subscribe(TOPIC, qos=1)
    print(f"subscribed topic={TOPIC}", flush=True)


def on_message(client, userdata, message):
    payload = message.payload.decode("utf-8")
    record = {
        "topic": message.topic,
        "payload": json.loads(payload),
        "received_at": datetime.now(timezone.utc).isoformat(),
    }
    redis_client.lpush(REDIS_KEY, json.dumps(record, ensure_ascii=False))
    redis_client.ltrim(REDIS_KEY, 0, 99)
    print(f"stored redis_key={REDIS_KEY} topic={message.topic} payload={payload}", flush=True)


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_HOST, MQTT_PORT, keepalive=30)
    client.loop_forever()


if __name__ == "__main__":
    main()
