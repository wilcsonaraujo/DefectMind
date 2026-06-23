from datetime import datetime
from pydantic import BaseModel


class HealthService(BaseModel):
    status: str
    service: str
    version: str
    environment: str
    database: str
    timestamp: datetime