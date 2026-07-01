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
    Story: Optional[int] = 0
    BugReport: Optional[int] = 0
    TestCase: Optional[int] = 0
    Requirement: Optional[int] = 0
    Incident: Optional[int] = 0
    PostMortem: Optional[int] = 0

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

