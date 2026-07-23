import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.src.core.database import get_db
from backend.src.core.dependencies import get_current_user
from backend.src.models.user import User
from backend.src.modules.users.schemas import UserResponse

router = APIRouter()


@router.get("/users", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):

    users = db.query(User).filter(User.is_active).all()
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
