import json
import time
import psycopg2
from kafka import KafkaConsumer

# This consumer connects to Kafka, listens for speed events, and writes them to Postgres.

# -------------------- DATABASE --------------------
conn = psycopg2.connect(
    host="db",
    dbname="speeds",
    user="postgres",
    password="postgres",
)
cur = conn.cursor()
print("✅ Connected to Postgres")

# -------------------- KAFKA (RETRY LOOP) --------------------
while True:
    try:
        consumer = KafkaConsumer(
            "speed-events",
            bootstrap_servers="kafka:9092",
            group_id="speed-db-writer",
            auto_offset_reset="latest",
            enable_auto_commit=True,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        )
        print("✅ Connected to Kafka")
        break
    except Exception as e:
        print("⏳ Kafka not ready, retrying...", e)
        time.sleep(5)

# -------------------- CONSUME & WRITE --------------------
for msg in consumer:
    e = msg.value
    print("📥 Writing to DB:", e)

    cur.execute(
        """
        INSERT INTO speed_readings(sensor_id, speed, ts)
        VALUES (%s, %s, to_timestamp(%s))
        """,
        (e["sensor_id"], e["speed"], e["ts"]),
    )
    conn.commit()
