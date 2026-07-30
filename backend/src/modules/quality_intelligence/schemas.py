from enum import Enum

from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    artifact: str
    type: str
    justification: str


class RiskLevelEnum(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class HealthScoreResponse(BaseModel):
    evidence: list[EvidenceItem]
    ai_analysis: str
    recommendations: list[str]
    risk_classification: RiskLevelEnum


class HealthScoreRequest(BaseModel):
    node_id: str


class HotspotItem(BaseModel):
    node_id: str
    title: str
    label: str = Field(default="Story", frozen=True)
    bug_count: int
    critical_bug_count: int
    incident_count: int
    postmortem_count: int
    score: float


class HotspotsResponse(BaseModel):
    hotspots: list[HotspotItem]
    total: int
    ai_analysis: str
    recommendations: list[str]


class GapType(str, Enum):
    NO_TEST_CASE = "NO_TEST_CASE"
    NO_FUNCTIONAL_COVERAGE = "NO_FUNCTIONAL_COVERAGE"
    ORPHAN_TEST_CASE = "ORPHAN_TEST_CASE"


class CoverageGap(BaseModel):
    node_id: str
    title: str
    label: str
    gap_type: GapType


class CoverageAnalysisResponse(BaseModel):
    coverage_score: float
    gaps: list[CoverageGap]
    ai_analysis: str
    recommendations: list[str]


class KnowledgeGapType(str, Enum):
    BUG_WITHOUT_TEST_CASE = "BUG_WITHOUT_TEST_CASE"
    INCIDENT_WITHOUT_POSTMORTEM = "INCIDENT_WITHOUT_POSTMORTEM"
    REQUIREMENT_WITHOUT_STORY = "REQUIREMENT_WITHOUT_STORY"
    STORY_WITHOUT_REQUIREMENT = "STORY_WITHOUT_REQUIREMENT"


class KnowledgeGap(BaseModel):
    node_id: str
    title: str
    label: str
    gap_type: KnowledgeGapType


class KnowledgeGapsResponse(BaseModel):
    gaps: list[KnowledgeGap]
    ai_analysis: str
    recommendations: list[str]


class VerdictEnum(str, Enum):
    READY = "READY"
    NEEDS_ATTENTION = "NEEDS_ATTENTION"
    NOT_READY = "NOT_READY"


class ReleaseReadinessRequest(BaseModel):
    story_ids: list[str] = Field(min_length=1)


class StoryReadiness(BaseModel):
    story_id: str
    title: str
    verdict: VerdictEnum
    incidents_count: int = Field(description="Incidents without postmortem count")
    coverage_score: float
    health_risk: RiskLevelEnum
    blockers: list[str]


class ReleaseReadinessResponse(BaseModel):
    results: list[StoryReadiness]
    ai_analysis: str
    recommendations: list[str]
