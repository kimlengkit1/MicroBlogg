from typing import Optional, Dict, Literal
from pydantic import BaseModel, Field

Status = Literal["healthy","unhealthy"]
class DependencyHealth(BaseModel):
    status: Status
    response_time_ms: Optional[float] = None
    error: Optional[str] = None
class HealthResponse(BaseModel):
    service: str
    status: Status
    dependencies: Dict[str, DependencyHealth]

class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    body: str = Field(..., min_length=1, max_length=100000)

class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    body: Optional[str]  = Field(None, min_length=1, max_length=100000)
