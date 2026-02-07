import { useEffect, useState } from "react";

export default function Speedometer() {
  const [speed, setSpeed] = useState(0);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:9000/ws/speed");

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setSpeed(data.speed);
    };

    ws.onerror = (err) => {
      console.error("WebSocket error", err);
    };

    return () => ws.close();
  }, []);

  return (
    <div>
      <h1>Speedometer</h1>
      <h2>{speed.toFixed(2)} km/h</h2>
    </div>
  );
}