from typing import Optional, Dict, Literal
from pydantic import BaseModel, Field

Status = Literal["healthy", "unhealthy"]

class DependencyHealth(BaseModel):
    status: Status
    response_time_ms: Optional[float] = None
    error: Optional[str] = None

class HealthResponse(BaseModel):
    service: str
    status: Status
    dependencies: Dict[str, DependencyHealth]

class CommentCreate(BaseModel):
    postId: str = Field(..., description="ID of the post being commented on")
    body: str = Field(..., min_length=1, max_length=10_000)

class CommentUpdate(BaseModel):
    body: Optional[str] = Field(None, min_length=1, max_length=10_000)
