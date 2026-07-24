from enum import Enum
from typing import Any

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
    filter: TypeEnum | None = None


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
    label: str
    properties: dict[str, Any]


class ImpactEdge(BaseModel):
    source: str
    target: str
    type: RelationTypeEnum


class ImpactAnalysisResponse(BaseModel):
    nodes: list[ImpactNode]
    edges: list[ImpactEdge]

class NodeByType(BaseModel):
    Story: int | None = 0
    BugReport: int | None = 0
    TestCase: int | None = 0
    Requirement: int | None = 0
    Incident: int | None = 0
    PostMortem: int | None = 0

class MostConnectedNode(BaseModel):
    id: str
    label: str
    title: str
    degree: int

class IsolatedNode(BaseModel):
    id: str
    label: str
    title: str

class StatsResponse(BaseModel):
    total_nodes: int
    total_edges: int
    nodes_by_type: NodeByType
    most_connected_nodes: list[MostConnectedNode]
    isolated_nodes: list[IsolatedNode]
    avg_degree: float
    density: float

