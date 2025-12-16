from typing import Optional, Literal, Dict
from pydantic import BaseModel, Field

# health models
Status = Literal["healthy", "unhealthy"]

class DependencyHealth(BaseModel):
    status: Status
    response_time_ms: Optional[float] = None
    error: Optional[str] = None

class HealthResponse(BaseModel):
    service: str
    status: Status
    dependencies: Dict[str, DependencyHealth] = Field(default_factory=dict)

# profile schemas
class ProfileOut(BaseModel):
    id: int
    auth_user_id: int
    display_name: Optional[str] = None
    bio: Optional[str] = None

class ProfileUpdate(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
