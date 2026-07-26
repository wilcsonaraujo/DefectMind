import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from neo4j import Session

logger = logging.getLogger(__name__)

from backend.src.core.ai.provider import AIProvider
from backend.src.core.ai.provider_factory import get_ai_provider
from backend.src.core.dependencies import get_current_user
from backend.src.core.neo4j_db import get_required_neo4j_session
from backend.src.models.user import User
from backend.src.modules.quality_intelligence.health_score_service import (
    HealthScoreService,
)
from backend.src.modules.quality_intelligence.schemas import (
    HealthScoreRequest,
    HealthScoreResponse,
)

router = APIRouter(dependencies=[Depends(get_current_user)])

Neo4jSession = Annotated[Session, Depends(get_required_neo4j_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
Provider = Annotated[AIProvider, Depends(get_ai_provider)]


@router.post(
    "/health-score",
    response_model=HealthScoreResponse,
    summary="Get the health score of the system",
)
def generate_health_score(
    generate: HealthScoreRequest,
    neo4j: Neo4jSession,
    provider: Provider,
    current_user: CurrentUser,
):
    service = HealthScoreService(neo4j_session=neo4j, ai_provider=provider)

    prompt = service.build_health_score_prompt(generate.node_id)

    if prompt is None:
        raise HTTPException(status_code=404, detail="Node not found.")

    try:
        return service.get_ai_response(prompt)
    except ValueError as e:
        logger.error(f"Failed to parse AI response for node {generate.node_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception:
        logger.exception(
            f"Unexpected error generating health score for node {generate.node_id}"
        )
        raise HTTPException(
            status_code=500, detail="Error occurred while generating health score."
        )
