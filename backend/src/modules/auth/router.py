import os
import datetime
from fastapi import APIRouter
from backend.src.core.config import settings
from backend.src.modules.auth.schemas import HealthService

router = APIRouter()


@router.get("/health", response_model=HealthService, summary="Health Check")
async def health_get_response():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.datetime.now(datetime.timezone.utc),
    }
