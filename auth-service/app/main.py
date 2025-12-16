import os, time
from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel, create_engine, Session, select
from pydantic import BaseModel
from .models import User
from .schemas import SignupIn, LoginIn, TokenOut, UserOut
from .security import hash_password, verify_password, make_access_token
from .health_models import HealthResponse, DependencyHealth

# DB setup (database-per-service)
DB_URL = os.getenv("DATABASE_URL", "sqlite:///data/auth.db")
engine = create_engine(DB_URL, connect_args={"check_same_thread": False} if DB_URL.startswith("sqlite") else {})

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(title="auth-service", lifespan=lifespan)

# dependency
def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

# health
@app.get("/health", response_model=HealthResponse)
async def health():
    t0 = time.perf_counter()
    try:
        # simple DB probe
        with Session(engine) as s:
            s.exec(select(User).limit(1)).all()
        overall = "healthy"
        db_health = DependencyHealth(status="healthy", response_time_ms=(time.perf_counter()-t0)*1000)
    except Exception as exc:
        overall = "unhealthy"
        db_health = DependencyHealth(status="unhealthy", error=str(exc), response_time_ms=(time.perf_counter()-t0)*1000)

    payload = HealthResponse(service="auth-service", status=overall, dependencies={"database": db_health})
    code = 200 if overall == "healthy" else 503
    return JSONResponse(status_code=code, content=payload.model_dump())

# alias for /health
@app.get("/auth/health", response_model=HealthResponse)
async def health_alias():
    return await health()

# auth endpoints
@app.post("/auth/signup", response_model=UserOut, status_code=201)
def signup(body: SignupIn, session: SessionDep):
    exists = session.exec(select(User).where(User.email == body.email)).first()
    if exists:
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(email=body.email, password_hash=hash_password(body.password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return UserOut(id=user.id, email=user.email)

@app.post("/auth/login", response_model=TokenOut)
def login(body: LoginIn, session: SessionDep):
    user = session.exec(select(User).where(User.email == body.email)).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = make_access_token(sub=str(user.id))
    return TokenOut(access_token=token)
