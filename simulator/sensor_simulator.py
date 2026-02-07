import time
import random
import requests

BACKEND_URL = "http://backend:8000/speed"

def wait_for_backend():
    while True:
        try:
            r = requests.get("http://backend:8000/docs", timeout=2)
            if r.status_code == 200:
                print("Backend is ready")
                return
        except Exception:
            print("Waiting for backend...")
            time.sleep(2)

wait_for_backend()

while True:
    try:
        requests.post(
            BACKEND_URL,
            json={
                "sensor_id": "robot-1",
                "speed": random.uniform(0, 120),
                "ts": time.time(),
            },
            timeout=2,
        )
        print("Speed sent")
    except Exception as e:
        print("Send failed, retrying...", e)

    time.sleep(1)
