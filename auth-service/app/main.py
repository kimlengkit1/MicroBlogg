import os, uuid, httpx
from fastapi import FastAPI, HTTPException, Depends, Header
from sqlmodel import select, Session
from datetime import datetime, timezone
from typing import Dict, Optional

from .db import init_db, get_session
from .models import User
from .schemas import SignupIn, LoginIn, TokenOut, UserOut, HealthResponse, DependencyHealth, Status
from .security import hash_password, verify_password, mint_token, verify_token

APP_NAME = "auth-service"
app = FastAPI(title=APP_NAME)

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health", response_model=HealthResponse)
def health():
    deps: Dict[str, DependencyHealth] = {}
    # DB touch
    try:
        for _ in get_session():
            pass
        db_status: Status = "healthy"
    except Exception as e:
        db_status = "unhealthy"
        deps["database"] = DependencyHealth(status="unhealthy", error=str(e))
    overall: Status = "healthy" if db_status == "healthy" else "unhealthy"
    return HealthResponse(service=APP_NAME, status=overall, dependencies=deps)

@app.post("/auth/signup", response_model=UserOut, status_code=201)
def signup(body: SignupIn, session: Session = Depends(get_session)):
    existing = session.exec(select(User).where(User.email == body.email)).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    u = User(id=str(uuid.uuid4()), email=body.email, password_hash=hash_password(body.password))
    session.add(u); session.commit(); session.refresh(u)
    return UserOut(id=u.id, email=u.email)

@app.post("/auth/login", response_model=TokenOut)
def login(body: LoginIn, session: Session = Depends(get_session)):
    u = session.exec(select(User).where(User.email == body.email)).first()
    if not u or not verify_password(body.password, u.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenOut(access_token=mint_token(u.id, u.email))

@app.post("/auth/verify")
def verify(payload: Dict):
    token = payload.get("token")
    if not token:
        raise HTTPException(status_code=400, detail="token required")
    try:
        claims = verify_token(token)
        return {"user_id": claims["sub"], "email": claims["email"]}
    except Exception:
        raise HTTPException(status_code=401, detail="invalid token")
