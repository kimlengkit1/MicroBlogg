from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone

class Profile(SQLModel, table=True):
    id: str = Field(primary_key=True, index=True)   # profile id
    userId: str = Field(unique=True, index=True)    # auth-service user id (1-1)
    display_name: str
    bio: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: Optional[str] = None
