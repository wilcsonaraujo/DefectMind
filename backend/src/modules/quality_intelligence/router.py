import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from neo4j import Session

from backend.src.modules.quality_intelligence.coverage_analysis_service import (
    CoverageAnalysisService,
)
from backend.src.modules.quality_intelligence.hotspots_service import HotspotsService
from backend.src.modules.quality_intelligence.knowledge_gaps_service import (
    KnowledgeGapsService,
)
from backend.src.modules.quality_intelligence.release_readiness_service import (
    ReleaseReadinessService,
    StoryNotFoundError,
)

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
    CoverageAnalysisResponse,
    HealthScoreRequest,
    HealthScoreResponse,
    HotspotsResponse,
    KnowledgeGapsResponse,
    ReleaseReadinessRequest,
    ReleaseReadinessResponse,
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


@router.get(
    "/hotspots",
    response_model=HotspotsResponse,
    summary="Get the hotspots of the system",
)
def generate_hotspots(
    neo4j: Neo4jSession,
    provider: Provider,
    current_user: CurrentUser,
    limit: int = Query(default=10, gt=0, le=100),
):
    service = HotspotsService(neo4j_session=neo4j, ai_provider=provider)

    try:
        return service.get_hotspots(limit)
    except ValueError as e:
        logger.error(f"Failed to parse AI response for hotspots: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception:
        logger.exception("Unexpected error generating hotspots")
        raise HTTPException(
            status_code=500, detail="Error occurred while generating hotspots."
        )


@router.get(
    "/coverage-analysis",
    response_model=CoverageAnalysisResponse,
    summary="Get the coverage gap of the system",
)
def generate_coverage(
    neo4j: Neo4jSession, provider: Provider, current_user: CurrentUser
):
    service = CoverageAnalysisService(neo4j_session=neo4j, ai_provider=provider)

    try:
        return service.get_coverage_analysis()
    except ValueError as e:
        logger.error(f"Failed to parse AI response for Coverage Gap: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception:
        logger.exception("Unexpected error generating coverage gap.")
        raise HTTPException(
            status_code=500, detail="Error occurred while generating coverage gap."
        )


@router.get(
    "/knowledge-gaps",
    response_model=KnowledgeGapsResponse,
    summary="Get the knowledge gap of the system",
)
def generate_knowledge_gap(
    neo4j: Neo4jSession, provider: Provider, current_user: CurrentUser
):
    service = KnowledgeGapsService(neo4j_session=neo4j, ai_provider=provider)

    try:
        return service.get_knowledge_gaps()
    except ValueError as e:
        logger.error(f"Failed to parse AI response for Knowledge Gap: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception:
        logger.exception("Unexpected error generating knowledge gap.")
        raise HTTPException(
            status_code=500, detail="Error occurred while generating knowledge gap."
        )


@router.post(
    "/release-readiness",
    response_model=ReleaseReadinessResponse,
    summary="Get the release readiness of the system",
)
def generate_release_readiness(
    generate: ReleaseReadinessRequest,
    neo4j: Neo4jSession,
    provider: Provider,
    current_user: CurrentUser,
):
    service = ReleaseReadinessService(neo4j_session=neo4j, ai_provider=provider)

    try:
        return service.get_release_readiness(generate.story_ids)
    except StoryNotFoundError as e:
        logger.error(f"Story(ies) not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        logger.error(f"Failed to parse AI response for Release Readiness: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception:
        logger.exception("Unexpected error generating Release Readiness.")
        raise HTTPException(
            status_code=500, detail="Error occurred while generating Release Readiness."
        )
