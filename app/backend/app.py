import os
from datetime import datetime, timezone

import redis
import requests
from flask import Flask, jsonify


app = Flask(__name__)


def redis_client():
    return redis.Redis(
        host=os.getenv("REDIS_HOST", "redis"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        password=os.getenv("REDIS_PASSWORD") or None,
        db=0,
        decode_responses=True,
        socket_connect_timeout=3,
        socket_timeout=3,
    )


@app.get("/api/ping")
def ping():
    return jsonify(
        {
            "status": "ok",
            "service": "cloud-course-backend",
            "time": datetime.now(timezone.utc).isoformat(),
        }
    )


@app.get("/api/visit")
def visit():
    client = redis_client()
    count = client.incr("visit_count")
    return jsonify({"status": "ok", "visit_count": count})


@app.get("/api/config")
def config():
    return jsonify(
        {
            "redis_host": os.getenv("REDIS_HOST", "redis"),
            "redis_port": os.getenv("REDIS_PORT", "6379"),
            "requests_version": requests.__version__,
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
