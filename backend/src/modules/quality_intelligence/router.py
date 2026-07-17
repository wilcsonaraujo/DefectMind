from fastapi import APIRouter, Depends
from backend.src.core.dependencies import get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])
