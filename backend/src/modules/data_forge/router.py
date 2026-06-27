from fastapi import APIRouter, Depends, Response
from backend.src.core.config import settings
from backend.src.core.dependencies import get_current_user
from backend.src.core.neo4j_db import get_neo4j_session
from backend.src.models.user import User
from backend.src.modules.data_forge.schemas import GenerateRequest


router = APIRouter()


@router.post("/data-forge/generate", summary="Instantiates the DataForgeService with injected dependencies and returns the counters.")
def instantiate_dataforgeservice(generate: GenerateRequest, neo4j=Depends(get_neo4j_session),
    current_user: User = Depends(get_current_user), gemini_key: str = settings.GEMINI_API_KEY):
    
    accountants = generate(generate.num_stories, generate.batch_size)

    return Response(content=accountants, media_type="application/json")