# 🚗 Real-Time Speedometer System (Production-Grade)

A **distributed, event-driven telemetry system** that ingests sensor data, stores time-series history, processes real-time state, and streams live updates to a web UI.

This project demonstrates **advanced backend system design** using Kafka, Redis, FastAPI, PostgreSQL, WebSockets, and Docker.

---

## 📌 High-Level Architecture

```
 Sensors / Simulator
        |
        v
 Ingestion API (FastAPI)
        |
        v
     Kafka Topic
   (speed-events)
        |
        +-----------------------------+
        |                             |
        v                             v
 DB Writer Consumer          Stream Processor
 (PostgreSQL / Timeseries)   (Latest state)
        |                             |
        v                             v
  Historical Data              Redis Pub/Sub
                                      |
                                      v
                             WebSocket Gateway
                                      |
                                      v
                                 Frontend UI
```

---

## 🧠 Design Philosophy

* **Kafka is the backbone** (durable, replayable, scalable)
* **Redis is for real-time fan-out**, not storage
* **PostgreSQL stores history**, not live state
* **WebSocket is isolated** from ingestion load
* **Frontend is stateless and disposable**

Each service has **one responsibility**.

---

## 📂 Folder Structure & Responsibilities

```
speedometer/
├── backend/                 # Ingestion API
│   ├── main.py               # POST /speed → Kafka
│   ├── Dockerfile
│   └── requirements.txt
│
├── db-writer/               # Kafka → PostgreSQL
│   ├── consumer.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── stream-processor/        # Kafka → Redis (latest)
│   ├── consumer.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── websocket-gateway/       # Redis → WebSocket
│   ├── main.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── simulator/               # Sensor simulator
│   ├── sensor_simulator.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                # React UI
│   ├── src/
│   ├── Dockerfile
│   └── package.json
│
├── infra/
│   └── postgres/
│       └── init.sql         # DB schema
│
├── docker-compose.yml
└── README.md
```

---

## 🔄 End-to-End Flow (Step by Step)

### 1️⃣ Sensor / Simulator

* Periodically sends speed data

```json
{
  "sensor_id": "sensor-1",
  "speed": 42,
  "ts": 1700000000
}
```

---

### 2️⃣ Backend – Ingestion API (FastAPI)

* Accepts HTTP requests
* Validates input
* Publishes event to Kafka

```python
producer.send("speed-events", event)
```

📌 Backend does **not** talk to Redis or WebSockets.

---

### 3️⃣ Kafka – Event Backbone

* Topic: `speed-events`
* Guarantees:

  * Durability
  * Ordering
  * Replay
  * Backpressure

Kafka decouples producers and consumers.

---

### 4️⃣ DB Writer – Historical Storage

* Kafka consumer
* Writes events to PostgreSQL

```sql
INSERT INTO speed_readings(sensor_id, speed, ts)
```

📌 Purpose: **time-series history & analytics**

---

### 5️⃣ Stream Processor – Real-Time State

* Kafka consumer
* Extracts latest speed
* Publishes to Redis

```python
redis.publish("speed-updates", speed)
```

📌 Purpose: **latest value only**

---

### 6️⃣ Redis – Real-Time Fan-out

* Pub/Sub channel: `speed-updates`
* Ultra-fast, in-memory
* No persistence (Kafka is source of truth)

---

### 7️⃣ WebSocket Gateway

* Subscribes to Redis
* Pushes updates to connected clients

```python
await ws.send_text(speed)
```

📌 Isolated from backend & Kafka load

---

### 8️⃣ Frontend (React)

* Connects via WebSocket

```js
ws://localhost:9000/ws/speed
```

* Updates UI in real time
* No business logic

---

## 🐞 Major Bugs We Hit (and Fixed)

### ❌ 1. Kafka `NoBrokersAvailable`

**Cause**

* Containers tried `localhost:9092`
* Kafka not ready at startup

**Fix**

* Use `kafka:9092`
* Add retry loops around KafkaProducer / KafkaConsumer

---

### ❌ 2. WebSocket 404 / Upgrade Failed

**Cause**

* `uvicorn` installed without WebSocket support

**Fix**

```txt
uvicorn[standard]
```

---

### ❌ 3. Frontend Showing `0 km/h`

**Cause**

* WebSocket payload not numeric
* React silently ignored invalid `Number()`

**Fix**

* Normalize payload before sending

---

### ❌ 4. WebSocket Connected to Wrong Service

**Cause**

* Frontend still pointed to backend (`8000`)
* WebSocket moved to gateway (`9000`)

**Fix**

```js
ws://localhost:9000/ws/speed
```

---

### ❌ 5. Multiple Kafka Consumers Created

**Cause**

* Duplicate `KafkaConsumer()` calls
* Missing `group_id`

**Fix**

* Single consumer
* Proper `group_id`
* Retry logic

---

## 🧪 How to Run on Linux (Clean Instructions)

### 1️⃣ Prerequisites

```bash
sudo apt update
sudo apt install -y docker.io docker-compose
sudo systemctl enable docker
sudo systemctl start docker
```

(Optional)

```bash
sudo usermod -aG docker $USER
logout
```

---

### 2️⃣ Clean Start (Recommended)

```bash
docker compose down -v --remove-orphans
docker system prune -a -f --volumes
```

---

### 3️⃣ Build & Start Everything

```bash
docker compose build --no-cache
docker compose up
```

---

### 4️⃣ Verify Services

```bash
docker compose ps
```

Expected:

* backend → 8000
* websocket-gateway → 9000
* frontend → 3000
* kafka → 9092
* redis → 6379
* postgres → 5432

---

### 5️⃣ Open UI

```
http://localhost:3000
```

You should see **live speed updates**.

---

### 6️⃣ Debugging Commands

```bash
docker compose logs -f backend
docker compose logs -f stream-processor
docker compose logs -f websocket-gateway
```

Manual Redis test:

```bash
docker exec -it speedometer-redis redis-cli
PUBLISH speed-updates 88
```

---

## 🎓 Why This Is Production-Grade

* Event-driven, not request-driven
* Horizontal scalability
* Clear separation of concerns
* Safe frontend deployments
* Replayable data
* Real-time + historical paths separated

This is **exactly how telemetry, IoT, fintech streams, and monitoring systems are built**.

---

## 🧠 One-Line Summary 

> “We built a real-time telemetry system using Kafka for durability, Redis for live state, PostgreSQL for time-series storage, and a dedicated WebSocket gateway for UI updates — fully decoupled and production-safe.”

---