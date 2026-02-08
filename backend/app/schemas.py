from pydantic import BaseModel
import time

# Pydantic model for speed events
class SpeedEvent(BaseModel):
    sensor_id: str
    speed: float
    ts: float = time.time()
