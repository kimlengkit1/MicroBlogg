import os, time, httpx
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel, select
from .deps import engine, SessionDep, get_current_user, AuthedUser
from .models import Post
from .schemas import (
    HealthResponse, DependencyHealth, PostCreate, PostUpdate, PostOut
)
from .cache import get_json, set_json, delete

AUTH_BASE = os.getenv("AUTH_SERVICE_BASE", "http://auth-service:8000")
USER_BASE = os.getenv("USER_SERVICE_BASE", "http://user-service:8000")
CACHE_TTL_SECONDS = int(os.getenv("POST_CACHE_TTL", "60"))

app = FastAPI(title="post-service")

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

# health (checks auth + user)
@app.get("/health", response_model=HealthResponse)
async def health():
    deps = {}
    overall = "healthy"

    async def probe(name: str, url: str):
        t0 = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.get(url)
                r.raise_for_status()
            deps[name] = DependencyHealth(status="healthy", response_time_ms=(time.perf_counter()-t0)*1000)
        except httpx.HTTPError as exc:
            nonlocal overall
            overall = "unhealthy"
            deps[name] = DependencyHealth(status="unhealthy", error=str(exc), response_time_ms=(time.perf_counter()-t0)*1000)

    await probe("auth-service", f"{AUTH_BASE}/health")
    await probe("user-service", f"{USER_BASE}/health")

    payload = HealthResponse(service="post-service", status=overall, dependencies=deps)
    return JSONResponse(status_code=200 if overall == "healthy" else 503, content=payload.model_dump())

# alias for nginx prefix preservation
@app.get("/posts/health", response_model=HealthResponse)
async def health_alias():
    return await health()

# whoami to verify load balancing via nginx
@app.get("/posts/whoami")
def whoami():
    return {"service": "post-service", "instance": os.getenv("HOSTNAME", "unknown")}

#  CRUD

# list posts (cache key only when default params)
@app.get("/posts", response_model=List[PostOut])
def list_posts(session: SessionDep, limit: int = 20, offset: int = 0):
    if limit == 20 and offset == 0:
        cache_key = "posts:list:limit20:offset0"
        cached = get_json(cache_key)
        if cached is not None:
            return cached

    stmt = select(Post).order_by(Post.created_at.desc()).offset(offset).limit(limit)
    rows = session.exec(stmt).all()
    out = [PostOut(id=p.id, author_auth_user_id=p.author_auth_user_id, title=p.title, body=p.body) for p in rows]

    if limit == 20 and offset == 0:
        set_json("posts:list:limit20:offset0", [o.model_dump() for o in out], CACHE_TTL_SECONDS)
    return out

# GET one post (cache-aside)
@app.get("/posts/{post_id}", response_model=PostOut)
def get_post(post_id: int, session: SessionDep):
    cache_key = f"post:{post_id}"
    cached = get_json(cache_key)
    if cached is not None:
        return cached

    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    out = PostOut(id=post.id, author_auth_user_id=post.author_auth_user_id, title=post.title, body=post.body)
    set_json(cache_key, out.model_dump(), CACHE_TTL_SECONDS)
    return out

# CREATE (requires JWT)
@app.post("/posts", response_model=PostOut, status_code=201)
def create_post(
    body: PostCreate,
    session: SessionDep,
    user: AuthedUser = Depends(get_current_user),
):
    post = Post(author_auth_user_id=user.user_id, title=body.title, body=body.body)
    session.add(post)
    session.commit()
    session.refresh(post)

    # invalidate caches
    delete("posts:list:limit20:offset0")
    delete(f"post:{post.id}")

    return PostOut(id=post.id, author_auth_user_id=post.author_auth_user_id, title=post.title, body=post.body)

# UPDATE (requires ownership)
@app.put("/posts/{post_id}", response_model=PostOut)
def update_post(
    post_id: int,
    patch: PostUpdate,
    session: SessionDep,
    user: AuthedUser = Depends(get_current_user),
):
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_auth_user_id != user.user_id:
        raise HTTPException(status_code=403, detail="Not your post")

    changed = False
    if patch.title is not None:
        post.title = patch.title
        changed = True
    if patch.body is not None:
        post.body = patch.body
        changed = True
    if changed:
        session.add(post)
        session.commit()
        session.refresh(post)

    # invalidate caches
    delete("posts:list:limit20:offset0")
    delete(f"post:{post.id}")

    return PostOut(id=post.id, author_auth_user_id=post.author_auth_user_id, title=post.title, body=post.body)

# DELETE (requires ownership)
@app.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: int, session: SessionDep, user: AuthedUser = Depends(get_current_user)):
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_auth_user_id != user.user_id:
        raise HTTPException(status_code=403, detail="Not your post")

    session.delete(post)
    session.commit()

    # invalidate caches
    delete("posts:list:limit20:offset0")
    delete(f"post:{post_id}")

    return JSONResponse(status_code=204, content=None)
