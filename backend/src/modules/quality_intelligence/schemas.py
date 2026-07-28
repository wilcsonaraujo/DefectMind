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
    NO_TEST_CASE = "no_test_case"
    NO_FUNCTIONAL_COVERAGE = "no_functional_coverage"
    ORPHAN_TEST_CASE = "orphan_test_case"


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
