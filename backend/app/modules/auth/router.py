import os
import datetime
from fastapi import APIRouter

from backend.app.modules.auth.schemas import HealthService

router = APIRouter()


@router.get("/health", response_model=HealthService, summary="Health Check")
async def health_get_response():
    return {
        "status": "healthy",
        "service": "DefectMind",
        "version": "1.0.0",
        "environment": "dev",
        "timestamp": datetime.datetime.now(datetime.timezone.utc),
    }
