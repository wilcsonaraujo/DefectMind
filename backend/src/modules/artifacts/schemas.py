from datetime import datetime
from enum import Enum
import uuid
from pydantic import BaseModel


class StoryRequest(BaseModel):
    title: str
    description: str


class StoryResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    created_at: datetime


class RequirementRequest(BaseModel):
    description: str
    priority: int


class RequirementResponse(BaseModel):
    id: uuid.UUID
    description: str
    priority: int
    created_at: datetime

class IncidentRequest(BaseModel):
    title: str
    description: str
    impact: int

class IncidentResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    impact: int
    created_at: datetime

class PostMortemRequest(BaseModel):
    root_cause: str
    resolution: str
    lessons_learned: str

class PostMortemResponse(BaseModel):
    id: uuid.UUID
    root_cause: str
    resolution: str
    lessons_learned: str
    created_at: datetime
