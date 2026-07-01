from enum import Enum
from typing import Any, Optional
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
    HAS_TESTCASE = "COVERED_BY"
    FOUND = "FOUND"
    CAUSED_INCIDENT = "CAUSED"
    HAS_POSTMORTEM = "ROOT_CAUSE"


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
