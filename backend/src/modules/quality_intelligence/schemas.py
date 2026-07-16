from pydantic.v1 import BaseModel


class EvidenceItem (BaseModel):
   artifact: str
   type: str
   justification: str

class RiskLevelEnum (BaseModel):
   LOW: str
   MEDIUM: str
   HIGH: str

class QIResponse (BaseModel):
   evidence: list[EvidenceItem]
   ai_analysis: str
   risk_classification: RiskLevelEnum