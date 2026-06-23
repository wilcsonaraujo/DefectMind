import os
import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from backend.src.core.config import settings
from backend.src.core.database import get_db
from backend.src.core.security import hash_password
from backend.src.models.user import User
from backend.src.modules.auth.schemas import HealthService, UserRegisterRequest, UserRegisterResponse

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

@router.post("/auth/register", response_model=UserRegisterResponse, status_code=201, summary="Register New User")
def user_register(payload: UserRegisterRequest, db: Session = Depends(get_db)):

    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    
    hashed = hash_password(payload.password)
    
    new_user = User(
        email=payload.email,
        hashed_password=hashed,
        full_name=payload.full_name,
        role=payload.role,           # Can be 'admin', 'analyst', or 'viewer'
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
