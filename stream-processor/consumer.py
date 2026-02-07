import json
import time
import redis
from kafka import KafkaConsumer

# -------------------- REDIS --------------------
r = redis.Redis(host="redis", decode_responses=True)
print("✅ Connected to Redis")

# -------------------- KAFKA (RETRY LOOP) --------------------
while True:
    try:
        consumer = KafkaConsumer(
            "speed-events",
            bootstrap_servers="kafka:9092",
            group_id="speed-stream-processor",
            auto_offset_reset="latest",
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        )
        print("✅ Connected to Kafka")
        break
    except Exception as e:
        print("⏳ Kafka not ready, retrying...", e)
        time.sleep(5)

# -------------------- PROCESS STREAM --------------------
for msg in consumer:
    event = msg.value
    print("📡 Publishing to Redis:", event)

    r.publish("speed-updates", json.dumps(event))
