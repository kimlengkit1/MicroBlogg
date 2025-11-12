import os
import time
from typing import Dict

import httpx
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.health_models import Status, DependencyHealth, HealthResponse

USER_SERVICE_BASE = os.getenv("USER_SERVICE_BASE", "http://user-service:8000")
POST_SERVICE_BASE = os.getenv("POST_SERVICE_BASE", "http://post-service:8000")

app = FastAPI(title="comment-service")

# helper to call another service's /health endpoint
# returns a DependencyHealth obj
async def check_dependency(base_url: str) -> DependencyHealth:

    start = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(f"{base_url}/health")
        elapsed_ms = (time.perf_counter() - start) * 1000

        if resp.status_code == 200:
            return DependencyHealth(status="healthy", response_time_ms=elapsed_ms)

        return DependencyHealth(status="unhealthy", response_time_ms=elapsed_ms)
    except httpx.RequestError as exc:
        elapsed_ms = (time.perf_counter() - start) * 1000
        return DependencyHealth(
            status="unhealthy",
            response_time_ms=elapsed_ms,
            error=str(exc),
        )

# comment depends on user and post
#report its own status but checks user and post status via their /health endpoints
@app.get("/health", response_model=HealthResponse)
async def health():
    dependencies: Dict[str, DependencyHealth] = {}

    # check user-service
    user_dep = await check_dependency(USER_SERVICE_BASE)
    dependencies["user-service"] = user_dep

    # check post-service
    post_dep = await check_dependency(POST_SERVICE_BASE)
    dependencies["post-service"] = post_dep

    # overall status is unhealthy if any dependency is unhealthy
    overall_status: Status = "healthy"
    for dep in dependencies.values():
        if dep.status == "unhealthy":
            overall_status = "unhealthy"
            break

    payload = HealthResponse(
        service="comment-service",
        status=overall_status,
        dependencies=dependencies,
    )

    http_status = 200 if overall_status == "healthy" else 503
    return JSONResponse(status_code=http_status, content=payload.model_dump())
