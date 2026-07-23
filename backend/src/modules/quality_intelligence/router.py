<<<<<<< HEAD
from fastapi import APIRouter, Depends, HTTPException
=======
from fastapi import APIRouter, Depends
from starlette.exceptions import HTTPException
>>>>>>> c6ae0462dfa3aa5f71c316fd23779e58ce1f57ab
from backend.src.core.ai.provider_factory import get_ai_provider
from backend.src.core.dependencies import get_current_user
from backend.src.core.neo4j_db import get_neo4j_session
from backend.src.modules.quality_intelligence.health_score_service import (
    HealthScoreService,
)
from backend.src.modules.quality_intelligence.schemas import (
    HealthScoreRequest,
    HealthScoreResponse,
)

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post(
    "/health-score",
    response_model=HealthScoreResponse,
    summary="Get the health score of the system",
)
def generate_health_score(
    generate: HealthScoreRequest,
    neo4j=Depends(get_neo4j_session),
    provider = Depends(get_ai_provider)
):
    service = HealthScoreService(neo4j_session=neo4j, ai_provider=provider)

    prompt = service.build_health_score_prompt(generate.node_id)
    
    if prompt is None:
        raise HTTPException(status_code=404, detail="Node don't found.")

    return service.get_ai_response(prompt)
