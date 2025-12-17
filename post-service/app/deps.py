import os
from typing import Annotated, Optional
from jose import jwt, JWTError
from fastapi import Depends, Header, HTTPException, status
from sqlmodel import Session, create_engine, SQLModel

DB_URL = os.getenv("DATABASE_URL", "sqlite:///data/post.db")
engine = create_engine(DB_URL, connect_args={"check_same_thread": False} if DB_URL.startswith("sqlite") else {})

def get_session():
    with Session(engine) as session:
        yield session
SessionDep = Annotated[Session, Depends(get_session)]

ALGO   = os.getenv("AUTH_ALGORITHM", "HS256")
SECRET = os.getenv("AUTH_SECRET_KEY", "dev-secret-change-me")

class AuthedUser:
    def __init__(self, user_id: int):
        self.user_id = user_id

def get_current_user(authorization: Optional[str] = Header(default=None)) -> AuthedUser:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGO])
        sub = payload.get("sub")
        if sub is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: no sub")
        return AuthedUser(int(sub))
    except (JWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
