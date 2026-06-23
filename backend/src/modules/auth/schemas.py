from datetime import datetime
from typing import Optional
import uuid
from pydantic import BaseModel, ConfigDict, EmailStr


class HealthService(BaseModel):
    status: str
    service: str
    version: str
    environment: str
    database: str
    timestamp: datetime

class UserRegisterRequest(BaseModel):
    full_name: Optional[str] = None
    email: EmailStr
    password: str

class UserRegisterResponse(BaseModel):
    id: uuid.UUID
    full_name: Optional[str] = None
    email: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
