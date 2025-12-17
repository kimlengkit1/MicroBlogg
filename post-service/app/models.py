from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class Post(SQLModel, table=True):
    __tablename__ = "posts"
    id: Optional[int] = Field(default=None, primary_key=True)
    author_auth_user_id: int = Field(index=True)
    title: str
    body: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
