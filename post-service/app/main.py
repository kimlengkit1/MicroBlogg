import os, uuid, httpx
from typing import Dict, Optional, List
from datetime import datetime, timezone

from fastapi import FastAPI, Depends, Header, HTTPException, Query
from sqlmodel import Session, select

from .db import init_db, get_session
from .models import Post
from .schemas import HealthResponse, DependencyHealth, Status, PostCreate, PostUpdate

APP_NAME = "post-service"
AUTH_SERVICE_BASE = os.getenv("AUTH_SERVICE_BASE", "http://auth-service:8000")
USER_SERVICE_BASE = os.getenv("USER_SERVICE_BASE", "http://user-service:8000")

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
        return r.json()  # {"user_id": "...", "email": "..."}    

@app.get("/health", response_model=HealthResponse)
async def health():
    deps: Dict[str, DependencyHealth] = {}
    # auth
    try:
        async with httpx.AsyncClient(timeout=5) as c:
            r = await c.get(f"{AUTH_SERVICE_BASE}/health")
            deps["auth-service"] = DependencyHealth(
                status="healthy" if r.status_code == 200 else "unhealthy",
                response_time_ms=None if r is None else None,
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

@app.post("/posts", status_code=201)
async def create_post(body: PostCreate, user=Depends(verify_token), session: Session = Depends(get_session)):
    p = Post(id=str(uuid.uuid4()), authorId=user["user_id"], title=body.title, body=body.body)
    session.add(p); session.commit(); session.refresh(p)
    return p

@app.get("/posts/{post_id}")
def get_post(post_id: str, session: Session = Depends(get_session)):
    p = session.get(Post, post_id)
    if not p: raise HTTPException(status_code=404, detail="Post not found")
    return p

@app.get("/posts")
def list_posts(limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0), session: Session = Depends(get_session)):
    rows = session.exec(select(Post).offset(offset).limit(limit)).all()
    return rows

@app.put("/posts/{post_id}")
def update_post(post_id: str, body: PostUpdate, user=Depends(verify_token), session: Session = Depends(get_session)):
    p = session.get(Post, post_id)
    if not p: raise HTTPException(status_code=404, detail="Post not found")
    if p.authorId != user["user_id"]: raise HTTPException(status_code=403, detail="Forbidden")
    if body.title is not None: p.title = body.title
    if body.body is not None:  p.body  = body.body
    p.updated_at = datetime.now(timezone.utc).isoformat()
    session.add(p); session.commit(); session.refresh(p)
    return p

@app.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: str, user=Depends(verify_token), session: Session = Depends(get_session)):
    p = session.get(Post, post_id)
    if not p: raise HTTPException(status_code=404, detail="Post not found")
    if p.authorId != user["user_id"]: raise HTTPException(status_code=403, detail="Forbidden")
    session.delete(p); session.commit()
    return None
