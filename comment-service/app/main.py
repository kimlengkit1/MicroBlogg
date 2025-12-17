import os, uuid
from datetime import datetime, timezone
from typing import Dict, Optional, List

import httpx
from fastapi import FastAPI, Depends, Header, HTTPException, Query, status
from sqlmodel import select, Session

from .db import init_db, get_session
from .models import Comment
from .schemas import (
    HealthResponse, DependencyHealth, Status,
    CommentCreate, CommentUpdate
)

APP_NAME = "comment-service"
AUTH_SERVICE_BASE = os.getenv("AUTH_SERVICE_BASE", "http://auth-service:8000")
POST_SERVICE_BASE = os.getenv("POST_SERVICE_BASE", "http://post-service:8000")

app = FastAPI(title=APP_NAME)

#startup
@app.on_event("startup")
def on_startup():
    init_db()

# helpers
async def verify_token_and_get_user(authorization: Optional[str] = Header(None)) -> Dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.split(" ", 1)[1]
    url = f"{AUTH_SERVICE_BASE}/auth/verify"
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            r = await client.post(url, json={"token": token})
            if r.status_code != 200:
                error_detail = r.json().get("detail", "Unknown error") if r.status_code < 500 else "Auth service error"
                raise HTTPException(status_code=401, detail=f"Invalid token: {error_detail}")
            return r.json()  # {"user_id": "...", "email": "..."}
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"auth-service unavailable: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")

async def ensure_post_exists(post_id: str) -> None:
    url = f"{POST_SERVICE_BASE}/posts/{post_id}"
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            r = await client.get(url)
            if r.status_code == 404:
                raise HTTPException(status_code=400, detail="Post does not exist")
            r.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise HTTPException(status_code=400, detail="Post does not exist")
            raise HTTPException(status_code=503, detail="post-service error")
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="post-service unavailable")

# health
@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    deps: Dict[str, DependencyHealth] = {}

    async with httpx.AsyncClient(timeout=5) as client:
        # auth-service
        try:
            start = datetime.now(timezone.utc)
            ar = await client.get(f"{AUTH_SERVICE_BASE}/health")
            ms = (datetime.now(timezone.utc) - start).total_seconds() * 1000
            deps["auth-service"] = DependencyHealth(
                status="healthy" if ar.status_code == 200 else "unhealthy",
                response_time_ms=round(ms, 2),
                error=None if ar.status_code == 200 else f"HTTP {ar.status_code}",
            )
        except Exception as e:
            deps["auth-service"] = DependencyHealth(status="unhealthy", response_time_ms=None, error=str(e))

        # post-service
        try:
            start = datetime.now(timezone.utc)
            pr = await client.get(f"{POST_SERVICE_BASE}/health")
            ms = (datetime.now(timezone.utc) - start).total_seconds() * 1000
            deps["post-service"] = DependencyHealth(
                status="healthy" if pr.status_code == 200 else "unhealthy",
                response_time_ms=round(ms, 2),
                error=None if pr.status_code == 200 else f"HTTP {pr.status_code}",
            )
        except Exception as e:
            deps["post-service"] = DependencyHealth(status="unhealthy", response_time_ms=None, error=str(e))

    # DB check (simple open session)
    try:
        for _ in get_session():
            pass
        db_status: Status = "healthy"
    except Exception as e:
        db_status = "unhealthy"
        deps["database"] = DependencyHealth(status="unhealthy", response_time_ms=None, error=str(e))

    overall: Status = "healthy" if all(d.status == "healthy" for d in deps.values()) and db_status == "healthy" else "unhealthy"
    return HealthResponse(service=APP_NAME, status=overall, dependencies=deps)

# CRUD
@app.post("/comments", status_code=201)
async def create_comment(
    payload: CommentCreate,
    user=Depends(verify_token_and_get_user),
    session: Session = Depends(get_session)
):
    await ensure_post_exists(payload.postId)
    cid = str(uuid.uuid4())
    c = Comment(
        id=cid,
        postId=payload.postId,
        authorId=user["user_id"],
        body=payload.body,
    )
    session.add(c)
    session.commit()
    session.refresh(c)
    return c

@app.get("/comments/{comment_id}")
def get_comment(comment_id: str, session: Session = Depends(get_session)):
    c = session.get(Comment, comment_id)
    if not c:
        raise HTTPException(status_code=404, detail="Comment not found")
    return c

@app.get("/comments")
def list_comments(
    postId: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session),
):
    stmt = select(Comment)
    if postId:
        stmt = stmt.where(Comment.postId == postId)
    rows = session.exec(stmt.offset(offset).limit(limit)).all()
    return rows

@app.put("/comments/{comment_id}")
def update_comment(
    comment_id: str,
    payload: CommentUpdate,
    user=Depends(verify_token_and_get_user),
    session: Session = Depends(get_session),
):
    c = session.get(Comment, comment_id)
    if not c:
        raise HTTPException(status_code=404, detail="Comment not found")
    if c.authorId != user["user_id"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    if payload.body is not None:
        c.body = payload.body
        c.updated_at = datetime.now(timezone.utc).isoformat()
    session.add(c)
    session.commit()
    session.refresh(c)
    return c

@app.delete("/comments/{comment_id}", status_code=204)
def delete_comment(
    comment_id: str,
    user=Depends(verify_token_and_get_user),
    session: Session = Depends(get_session),
):
    c = session.get(Comment, comment_id)
    if not c:
        raise HTTPException(status_code=404, detail="Comment not found")
    if c.authorId != user["user_id"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    session.delete(c)
    session.commit()
    return None
