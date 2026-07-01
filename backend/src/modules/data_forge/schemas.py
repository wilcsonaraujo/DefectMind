from enum import Enum
from typing import List
from pydantic import BaseModel


class PriorityEnum(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class ImpactEnum(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class SeverityEnum(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class PostMortem(BaseModel):
    temp_id: int
    incident_temp_id: int
    title: str
    root_cause: str
    resolution: str
    lessons_learned: str


class Incident(BaseModel):
    temp_id: int
    bug_temp_id: int
    title: str
    description: str
    impact: ImpactEnum


class BugReport(BaseModel):
    temp_id: int
    testcase_temp_id: int
    title: str
    description: str
    severity: SeverityEnum


class TestCase(BaseModel):
    temp_id: int
    requirement_temp_id: int
    title: str
    steps: str
    expected_result: str


class Requirement(BaseModel):
    temp_id: int
    story_temp_id: int
    title: str
    description: str
    priority: PriorityEnum


class Story(BaseModel):
    temp_id: int
    title: str
    description: str


class DataForgeOutput(BaseModel):
    stories: List[Story]
    requirements: List[Requirement]
    testcases: List[TestCase]
    bug_reports: List[BugReport]
    incidents: List[Incident]
    postmortems: List[PostMortem]


class GenerateRequest(BaseModel):
    num_stories: int = 20
    batch_size: int = 5
