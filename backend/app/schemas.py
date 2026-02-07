from pydantic import BaseModel
import time

class SpeedEvent(BaseModel):
    sensor_id: str
    speed: float
    ts: float = time.time()
