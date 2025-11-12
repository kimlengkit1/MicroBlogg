from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.health_models import HealthResponse

app = FastAPI(title="auth-service")

# auth has no dependencies so it just reports itself as healthy
@app.get("/health", response_model=HealthResponse)
async def health():
    payload = HealthResponse(
        service="auth-service",
        status="healthy",
        dependencies={}
    )
    return JSONResponse(status_code=200, content=payload.model_dump())