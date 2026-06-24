from datetime import datetime
from typing import Optional
import uuid
from pydantic import BaseModel


class StoryRequest(BaseModel):
    title: str
    description: str
    created_at: datetime

class StoryResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    created_at: datetime

class RequirementRequest(BaseModel):
    description: str
    priority: int
    created_at: datetime

class RequirementResponse(BaseModel):
    id: uuid.UUID
    description: str
    priority: int
    created_at: datetime