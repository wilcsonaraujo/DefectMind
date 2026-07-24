import uuid
from datetime import datetime
from enum import Enum

import neo4j
from pydantic import BaseModel, field_validator


class BaseResponse(BaseModel):
    @field_validator("created_at", mode="before", check_fields=False)
    @classmethod
    def parse_datetime(cls, v):
        if isinstance(v, neo4j.time.DateTime):
            return v.to_native()
        return v


class StoryRequest(BaseModel):
    title: str
    description: str


class StoryResponse(BaseResponse):
    id: uuid.UUID
    title: str
    description: str
    created_at: datetime


class PriorityEnum(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class RequirementRequest(BaseModel):
    title: str
    description: str
    priority: PriorityEnum


class RequirementResponse(BaseResponse):
    id: uuid.UUID
    title: str
    description: str
    priority: PriorityEnum
    created_at: datetime


class TestCaseRequest(BaseModel):
    title: str
    steps: str
    expected_result: str


class TestCaseResponse(BaseResponse):
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


class BugReportResponse(BaseResponse):
    id: uuid.UUID
    title: str
    description: str
    severity: SeverityEnum
    created_at: datetime


class ImpactEnum(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class IncidentRequest(BaseModel):
    title: str
    description: str
    impact: ImpactEnum


class IncidentResponse(BaseResponse):
    id: uuid.UUID
    title: str
    description: str
    impact: ImpactEnum
    created_at: datetime


class PostMortemRequest(BaseModel):
    title: str
    root_cause: str
    resolution: str
    lessons_learned: str


class PostMortemResponse(BaseResponse):
    id: uuid.UUID
    title: str
    root_cause: str
    resolution: str
    lessons_learned: str
    created_at: datetime


class RelationshipRequest(BaseModel):
    message: str
    from_id: str
    to_id: str
    relationship_type: str
