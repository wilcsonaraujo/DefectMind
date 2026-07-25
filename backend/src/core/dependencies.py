from typing import Annotated
import uuid
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from backend.src.core.database import get_db
from backend.src.core.embeddings.embedding_service import EmbeddingService
from backend.src.core.security import decode_access_token
from backend.src.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

DatabaseSession = Annotated[Session, Depends(get_db)]

def validate_current_user(token: str, db: Session) -> User:
    """Validate the current user from the token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        user_uuid = uuid.UUID(user_id)
    except (JWTError, ValueError):
        raise credentials_exception

    user = db.query(User).filter(User.id == user_uuid).first()
    if user is None or not user.is_active:
        raise credentials_exception

    return user

def get_current_user(
    db: DatabaseSession,
    token: str = Depends(oauth2_scheme)    
) -> User:
    """Get the current user from the token."""
    return validate_current_user(token, db)

@lru_cache(maxsize=1)
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()
