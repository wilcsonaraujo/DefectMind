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


class testCaseRequest(BaseModel):
    title: str
    steps: str
    expected_result: str


class testCaseResponse(BaseModel):
    id: uuid.UUID
    title: str
    steps: str
    expected_result: str
    created_at: datetime


class statusEnum(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class bugReportRequest(BaseModel):
    title: str
    description: str
    severity: int
    status: statusEnum


class bugReportResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    severity: int
    status: statusEnum
    created_at: datetime
