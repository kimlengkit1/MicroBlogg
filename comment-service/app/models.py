from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone

class Comment(SQLModel, table=True):
    id: str = Field(primary_key=True, index=True)
    postId: str = Field(index=True)
    authorId: str = Field(index=True)
    body: str
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: Optional[str] = None
