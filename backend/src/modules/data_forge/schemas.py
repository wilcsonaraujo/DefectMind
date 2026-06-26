from enum import Enum
from typing import List
from pydantic import BaseModel


class PostMortem(BaseModel):
    temp_id: int
    incident_temp_id: int
    root_cause: str
    resolution: str
    lessons_learned: str


class ImpactEnum(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class Incident(BaseModel):
    temp_id: int
    bug_temp_id: int
    title: str
    description: str
    impact: ImpactEnum


class SeverityEnum(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


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

class PriorityEnum(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class Requirement(BaseModel):
    temp_id: int
    story_temp_id: int
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
    bugsreport: List[BugReport]
    incidents: List[Incident]
    postmortems: List[PostMortem]
