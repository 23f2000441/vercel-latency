from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import numpy as np
from pathlib import Path

app = FastAPI()

# ✅ CORRECT CORS (POST + OPTIONS, any origin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

DATA_PATH = Path(__file__).resolve().parent.parent / "q-vercel-latency.json"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    TELEMETRY = json.load(f)

@app.post("/api")
async def latency_metrics(request: Request):
    body = await request.json()
    regions = body["regions"]
    threshold = body["threshold_ms"]

    result = {}

    for region in regions:
        records = [r for r in TELEMETRY if r["region"] == region]
        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime_pct"] for r in records]

        result[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": sum(1 for l in latencies if l > threshold),
        }

    return result
