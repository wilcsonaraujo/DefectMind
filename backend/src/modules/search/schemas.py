from enum import Enum
from typing import Any, Optional
import uuid
from pydantic import BaseModel, Field


class TypeEnum(str, Enum):
    STORY = "Story"
    REQUIREMENT = "Requirement"
    TESTCASE = "TestCase"
    BUGREPORT = "BugReport"
    INCIDENT = "Incident"
    POSTMORTEM = "PostMortem"


class RelationTypeEnum(str, Enum):
    HAS_REQUIREMENT = "HAS_REQUIREMENT"
    HAS_TESTCASE = "HAS_TESTCASE"
    FOUND_BUG = "FOUND_BUG"
    CAUSED_INCIDENT = "CAUSED_INCIDENT"
    HAS_POSTMORTEM = "HAS_POSTMORTEM"


class SemanticSearchRequest(BaseModel):
    request_text: str
    limit_responses: int = Field(gt=0, default=10)
    filter: Optional[TypeEnum] = None


class SearchResult(BaseModel):
    id: str
    label: TypeEnum
    properties: dict[str, Any]
    score: float


class SemanticSearchResponse(BaseModel):
    results: list[SearchResult]
    total: int


class ImpactNode(BaseModel):
    id: str
    label: TypeEnum
    properties: dict[str, Any]


class ImpactEdge(BaseModel):
    source: str
    target: str
    type: RelationTypeEnum


class ImpactAnalysisResponse(BaseModel):
    nodes: list[ImpactNode]
    edges: list[ImpactEdge]
