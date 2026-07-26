import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class HealthService(BaseModel):
    status: str
    service: str
    version: str
    environment: str
    database: str
    neo4j: str
    timestamp: datetime

class UserRegisterRequest(BaseModel):
    full_name: str | None = None
    email: EmailStr
    password: str
    role: str | None = "viewer"  # Default role is 'viewer'

class UserRegisterResponse(BaseModel):
    id: uuid.UUID
    full_name: str | None = None
    email: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds until the token expires
