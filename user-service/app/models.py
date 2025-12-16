from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, UniqueConstraint

class UserProfile(SQLModel, table=True):
    __tablename__ = "user_profiles"
    __table_args__ = (UniqueConstraint("auth_user_id", name="uq_profiles_auth_user_id"),)
    id: Optional[int] = Field(default=None, primary_key=True)
    auth_user_id: int = Field(index=True)  # id from auth-service
    display_name: Optional[str] = None
    bio: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
