import time, json
from fastapi import FastAPI
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
from .schemas import SpeedEvent

app = FastAPI()
producer = None

# Kafka producer is initialized lazily to allow the app to start even if Kafka is not ready yet
def get_producer():
    global producer
    if producer:
        return producer

    for _ in range(10):
        try:
            producer = KafkaProducer(
                bootstrap_servers="kafka:9092",
                value_serializer=lambda v: json.dumps(v).encode(),
                key_serializer=lambda k: k.encode(),
                api_version_auto_timeout_ms=3000,
            )
            print("Kafka producer connected")
            return producer
        except NoBrokersAvailable:
            print("Kafka not ready, retrying...")
            time.sleep(2)

    raise RuntimeError("Kafka not available")

# Endpoint to receive speed events and publish them to Kafka
@app.post("/speed")
def ingest(event: SpeedEvent):
    p = get_producer()
    p.send(
        "speed-events",
        key=event.sensor_id,
        value=event.model_dump()
    )
    return {"status": "accepted"}
