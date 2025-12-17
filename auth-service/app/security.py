import os, jwt
import bcrypt
from datetime import datetime, timedelta, timezone

# Use AUTH_SECRET_KEY to match docker-compose.yml, fallback to JWT_SECRET for backwards compatibility
JWT_SECRET = os.getenv("AUTH_SECRET_KEY") or os.getenv("JWT_SECRET", "dev-secret")
JWT_ALG = os.getenv("AUTH_ALGORITHM", "HS256")
JWT_TTL_MIN = int(os.getenv("JWT_TTL_MIN", "60"))

def hash_password(raw: str) -> str:
    # bcrypt limit: 72 bytes - encode to bytes and truncate if needed
    password_bytes = raw.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Return as string (bcrypt hash is ASCII-safe)
    return hashed.decode('utf-8')

def verify_password(raw: str, hashed: str) -> bool:
    # bcrypt limit: 72 bytes - encode to bytes and truncate if needed
    password_bytes = raw.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    # Verify password
    hashed_bytes = hashed.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)

def mint_token(user_id: str, email: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": user_id, "email": email, "iat": int(now.timestamp()),
               "exp": int((now + timedelta(minutes=JWT_TTL_MIN)).timestamp())}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def verify_token(token: str):
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
