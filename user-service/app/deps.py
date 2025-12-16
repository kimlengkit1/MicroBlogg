import os
from typing import Annotated
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from sqlmodel import Session, create_engine
from .models import SQLModel

ALGO = os.getenv("AUTH_ALGORITHM", "HS256")
SECRET = os.getenv("AUTH_SECRET_KEY", "dev-secret-change-me")

# DB
DB_URL = os.getenv("DATABASE_URL", "sqlite:///data/user.db")
engine = create_engine(DB_URL, connect_args={"check_same_thread": False} if DB_URL.startswith("sqlite") else {})

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

# JWT
class AuthedUser:
    def __init__(self, user_id: int):
        self.user_id = user_id

def get_current_user(authorization: str | None = None) -> AuthedUser:
    """
    Expects header: Authorization: Bearer <token>
    Token must have sub = auth_user_id (stringified int)
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGO])
        sub = payload.get("sub")
        if sub is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: no sub")
        return AuthedUser(user_id=int(sub))
    except (JWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
