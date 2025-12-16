import os, time, httpx
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel, select
from .deps import engine, SessionDep, get_current_user, AuthedUser
from .models import UserProfile
from .schemas import HealthResponse, DependencyHealth, ProfileOut, ProfileUpdate

AUTH_BASE = os.getenv("AUTH_SERVICE_BASE", "http://auth-service:8000")

app = FastAPI(title="user-service")

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

# health (with dependency probe to auth-service)
@app.get("/health", response_model=HealthResponse)
async def health():
    deps = {}
    overall = "healthy"
    t0 = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{AUTH_BASE}/health")
            r.raise_for_status()
        deps["auth-service"] = DependencyHealth(status="healthy", response_time_ms=(time.perf_counter()-t0)*1000)
    except httpx.HTTPError as exc:
        overall = "unhealthy"
        deps["auth-service"] = DependencyHealth(
            status="unhealthy",
            error=str(exc),
            response_time_ms=(time.perf_counter()-t0)*1000
        )

    payload = HealthResponse(service="user-service", status=overall, dependencies=deps)
    code = 200 if overall == "healthy" else 503
    return JSONResponse(status_code=code, content=payload.model_dump())

# alias so /users/health works behind nginx with preserved prefix
@app.get("/users/health", response_model=HealthResponse)
async def health_alias():
    return await health()

# profiles
@app.get("/users/me", response_model=ProfileOut)
def get_me(
    session: SessionDep,
    authorization: Optional[str] = Header(default=None),
):
    user = get_current_user(authorization)
    prof = session.exec(select(UserProfile).where(UserProfile.auth_user_id == user.user_id)).first()
    if not prof:
        # auto-provision a blank profile on first read
        prof = UserProfile(auth_user_id=user.user_id)
        session.add(prof)
        session.commit()
        session.refresh(prof)
    return ProfileOut(id=prof.id, auth_user_id=prof.auth_user_id, display_name=prof.display_name, bio=prof.bio)

@app.put("/users/me", response_model=ProfileOut)
def update_me(
    body: ProfileUpdate,
    session: SessionDep,
    authorization: Optional[str] = Header(default=None),
):
    user = get_current_user(authorization)
    prof = session.exec(select(UserProfile).where(UserProfile.auth_user_id == user.user_id)).first()
    if not prof:
        prof = UserProfile(auth_user_id=user.user_id)
        session.add(prof)
        session.commit()
        session.refresh(prof)
    changed = False
    if body.display_name is not None:
        prof.display_name = body.display_name
        changed = True
    if body.bio is not None:
        prof.bio = body.bio
        changed = True
    if changed:
        session.add(prof)
        session.commit()
        session.refresh(prof)
    return ProfileOut(id=prof.id, auth_user_id=prof.auth_user_id, display_name=prof.display_name, bio=prof.bio)

@app.get("/users/{profile_id}", response_model=ProfileOut)
def get_by_id(profile_id: int, session: SessionDep):
    prof = session.get(UserProfile, profile_id)
    if not prof:
        raise HTTPException(status_code=404, detail="Profile not found")
    return ProfileOut(id=prof.id, auth_user_id=prof.auth_user_id, display_name=prof.display_name, bio=prof.bio)
