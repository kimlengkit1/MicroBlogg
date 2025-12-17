import os, uuid, httpx
from typing import Dict, Optional
from datetime import datetime, timezone

from fastapi import FastAPI, Depends, Header, HTTPException
from sqlmodel import Session, select

from .db import init_db, get_session
from .models import Profile
from .schemas import HealthResponse, DependencyHealth, Status, ProfileCreate, ProfileUpdate

APP_NAME = "user-service"
AUTH_SERVICE_BASE = os.getenv("AUTH_SERVICE_BASE", "http://auth-service:8000")

app = FastAPI(title=APP_NAME)

@app.on_event("startup")
def startup():
    init_db()

async def verify_token(authorization: Optional[str] = Header(None)) -> Dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.split(" ", 1)[1]
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(f"{AUTH_SERVICE_BASE}/auth/verify", json={"token": token})
        if r.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid token")
        return r.json()

@app.get("/health", response_model=HealthResponse)
async def health():
    deps: Dict[str, DependencyHealth] = {}
    # auth-service
    try:
        async with httpx.AsyncClient(timeout=5) as c:
            r = await c.get(f"{AUTH_SERVICE_BASE}/health")
            deps["auth-service"] = DependencyHealth(
                status="healthy" if r.status_code == 200 else "unhealthy",
                error=None if r.status_code == 200 else f"HTTP {r.status_code}",
            )
    except Exception as e:
        deps["auth-service"] = DependencyHealth(status="unhealthy", error=str(e))
    # db
    try:
        for _ in get_session(): pass
        db_ok = True
    except Exception as e:
        deps["database"] = DependencyHealth(status="unhealthy", error=str(e))
        db_ok = False
    overall: Status = "healthy" if all(d.status=="healthy" for d in deps.values()) and db_ok else "unhealthy"
    return HealthResponse(service=APP_NAME, status=overall, dependencies=deps)

# Minimal profile API used by others to validate existence
@app.post("/users/me/profile", status_code=201)
def upsert_my_profile(body: ProfileCreate, user=Depends(verify_token), session: Session = Depends(get_session)):
    prof = session.exec(select(Profile).where(Profile.userId == user["user_id"])).first()
    if prof:
        prof.display_name = body.display_name
        prof.bio = body.bio
        prof.updated_at = datetime.now(timezone.utc).isoformat()
    else:
        prof = Profile(id=str(uuid.uuid4()), userId=user["user_id"], display_name=body.display_name, bio=body.bio)
        session.add(prof)
    session.commit(); session.refresh(prof)
    return prof

@app.get("/users/{user_id}")
def get_profile_by_user_id(user_id: str, session: Session = Depends(get_session)):
    prof = session.exec(select(Profile).where(Profile.userId == user_id)).first()
    if not prof:
        raise HTTPException(status_code=404, detail="User profile not found")
    return prof
