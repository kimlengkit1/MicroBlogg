from typing import Dict, Optional, Literal
from pydantic import BaseModel, Field

Status = Literal["healthy", "unhealthy"]

class DependencyHealth(BaseModel):
    status: Status
    response_time_ms: Optional[float] = Field(default=None)
    error: Optional[str] = Field(default=None)


class HealthResponse(BaseModel):
    service: str
    status: Status
    dependencies: Dict[str, DependencyHealth] = Field(default_factory=dict)