import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from backend.src.core.config import settings
from backend.src.core.database import get_db
from backend.src.core.dependencies import get_current_user
from backend.src.core.neo4j_db import get_neo4j_session
from backend.src.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from backend.src.models.user import User
from backend.src.modules.auth.schemas import (
    HealthService,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserRegisterResponse,
)

router = APIRouter()


@router.get("/health", response_model=HealthService, summary="Health Check")
async def health_get_response(db: Session = Depends(get_db), neo4j=Depends(get_neo4j_session)):
    db.execute(text("SELECT 1"))
    
    neo4j_status = "disconnected"
    if neo4j is not None:
        neo4j.run("RETURN 1")
        neo4j_status = "connected"
    
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "database": "connected",
        "neo4j": neo4j_status,
        "timestamp": datetime.datetime.now(datetime.timezone.utc),
    }


@router.post(
    "/auth/register",
    response_model=UserRegisterResponse,
    status_code=201,
    summary="Register New User",
)
def user_register(payload: UserRegisterRequest, db: Session = Depends(get_db)):

    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    hashed = hash_password(payload.password)

    new_user = User(
        email=payload.email,
        hashed_password=hashed,
        full_name=payload.full_name,
        role=payload.role,  # Can be 'admin', 'analyst', or 'viewer'
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/auth/login", summary="User Login", response_model=TokenResponse)
def user_login(payload: UserLoginRequest, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == payload.email).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is inactive")

    # Here you would generate a JWT token or similar
    token = create_access_token(str(user.id), user.role)

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.get("/auth/me", response_model=UserRegisterResponse, summary="Get Current User")
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
