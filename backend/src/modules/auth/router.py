import os
import datetime
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from backend.src.core.config import settings
from backend.src.core.database import get_db
from backend.src.modules.auth.schemas import HealthService

router = APIRouter()


@router.get("/health", response_model=HealthService, summary="Health Check")
async def health_get_response(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "database": "connected",
        "timestamp": datetime.datetime.now(datetime.timezone.utc),
    }
