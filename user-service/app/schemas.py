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

class ProfileCreate(BaseModel):
    display_name: str = Field(..., min_length=1, max_length=80)
    bio: Optional[str] = Field(None, max_length=1000)

class ProfileUpdate(BaseModel):
    display_name: Optional[str] = Field(None, min_length=1, max_length=80)
    bio: Optional[str] = Field(None, max_length=1000)
