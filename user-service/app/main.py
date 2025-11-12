import os
import time
from typing import Dict
import httpx
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.health_models import Status, DependencyHealth, HealthResponse

AUTH_SERVICE_BASE = os.getenv("AUTH_SERVICE_BASE", "http://auth-service:8000")

app = FastAPI(title="user-service")

# user depends on auth and uses httpx to call its /health
@app.get("/health", response_model=HealthResponse)
async def health():
    overall_status: Status = "healthy"
    dependencies: Dict[str, DependencyHealth] = {}

    # check auth
    start = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(f"{AUTH_SERVICE_BASE}/health")
        elapsed_ms = (time.perf_counter() - start) * 1000

        if resp.status_code == 200:
            dep_status: Status = "healthy"
        else:
            dep_status = "unhealthy"
            overall_status = "unhealthy"

        dependencies["auth-service"] = DependencyHealth(
            status=dep_status,
            response_time_ms=elapsed_ms,
        )
    except httpx.RequestError as exc:
        elapsed_ms = (time.perf_counter() - start) * 1000
        overall_status = "unhealthy"
        dependencies["auth-service"] = DependencyHealth(
            status="unhealthy",
            response_time_ms=elapsed_ms,
            error=str(exc),
        )

    payload = HealthResponse(
        service="user-service",
        status=overall_status,
        dependencies=dependencies,
    )

    http_status = 200 if overall_status == "healthy" else 503
    return JSONResponse(status_code=http_status, content=payload.model_dump())