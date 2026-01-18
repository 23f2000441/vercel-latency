from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
import json
import numpy as np
from pathlib import Path

app = FastAPI()

DATA_PATH = Path(__file__).resolve().parent.parent / "q-vercel-latency.json"
with open(DATA_PATH, "r", encoding="utf-8") as f:
    TELEMETRY = json.load(f)

def cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
    }

@app.get("/")
def health():
    # so opening base URL in browser shows something
    return {"status": "ok", "hint": "POST to /api"}

@app.options("/api")
def options_api():
    # Preflight response (must include CORS headers)
    return Response(status_code=204, headers=cors_headers())

@app.post("/api")
async def latency_metrics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 180)

    out = {}
    for region in regions:
        records = [r for r in TELEMETRY if r["region"] == region]
        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime_pct"] for r in records]

        out[region] = {
            "avg_latency": float(np.mean(latencies)) if latencies else 0.0,
            "p95_latency": float(np.percentile(latencies, 95)) if latencies else 0.0,
            "avg_uptime": float(np.mean(uptimes)) if uptimes else 0.0,
            "breaches": int(sum(1 for l in latencies if l > threshold)),
        }

    # Return JSON with explicit CORS headers
    return JSONResponse(content=out, headers=cors_headers())
