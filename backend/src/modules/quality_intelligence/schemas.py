from enum import Enum
from pydantic import BaseModel


class EvidenceItem (BaseModel):
   artifact: str
   type: str
   justification: str

class RiskLevelEnum (str, Enum):
   LOW: str
   MEDIUM: str
   HIGH: str

class QIResponse (BaseModel):
   evidence: list[EvidenceItem]
   ai_analysis: str
   risk_classification: RiskLevelEnum