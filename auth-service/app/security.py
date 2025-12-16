import os
from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext

ALGO = os.getenv("AUTH_ALGORITHM", "HS256")
SECRET = os.getenv("AUTH_SECRET_KEY", "dev-secret-change-me")
ACCESS_MIN = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(raw: str) -> str:
    return pwd.hash(raw)

def verify_password(raw: str, hashed: str) -> bool:
    return pwd.verify(raw, hashed)

def make_access_token(sub: str) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=ACCESS_MIN)
    payload = {"sub": sub, "iat": int(now.timestamp()), "exp": int(exp.timestamp())}
    return jwt.encode(payload, SECRET, algorithm=ALGO)
