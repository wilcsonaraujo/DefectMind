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


class TestCaseRequest(BaseModel):
    title: str
    steps: str
    expected_result: str


class TestCaseResponse(BaseModel):
    id: uuid.UUID
    title: str
    steps: str
    expected_result: str
    created_at: datetime


class SeverityEnum(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class BugReportRequest(BaseModel):
    title: str
    description: str
    severity: SeverityEnum


class BugReportResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    severity: SeverityEnum
    created_at: datetime
