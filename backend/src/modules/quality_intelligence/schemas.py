from enum import Enum
from pydantic import BaseModel


class EvidenceItem (BaseModel):
   artifact: str
   type: str
   justification: str

class RiskLevelEnum (str, Enum):
   LOW = "LOW"
   MEDIUM = "MEDIUM"
   HIGH = "HIGH"

class HealthScoreResponse (BaseModel):
   evidence: list[EvidenceItem]
   ai_analysis: str
   recommendations: list[str]
   risk_classification: RiskLevelEnum

class HealthScoreRequest (BaseModel):
   node_id: str
