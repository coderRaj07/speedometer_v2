import json
import redis.asyncio as redis
from fastapi import FastAPI, WebSocket

app = FastAPI()
r = redis.Redis(host="redis", decode_responses=True)

# WebSocket endpoint for real-time speed updates to the frontend
@app.websocket("/ws/speed")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()

    pubsub = r.pubsub()
    await pubsub.subscribe("speed-updates")

    async for msg in pubsub.listen():
        if msg["type"] == "message":
            # msg["data"] is already JSON string
            await ws.send_text(msg["data"])
