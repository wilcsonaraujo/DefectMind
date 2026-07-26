import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from neo4j import Session

from backend.src.core.dependencies import get_current_user, get_embedding_service
from backend.src.core.embeddings.embedding_service import (
    EmbeddingService as EmbeddingServiceType,
)
from backend.src.core.neo4j_db import get_required_neo4j_session
from backend.src.models.user import User
from backend.src.modules.search.graph import GraphService
from backend.src.modules.search.impact_analysis_service import ImpactAnalysisService
from backend.src.modules.search.schemas import (
    ImpactAnalysisResponse,
    SemanticSearchRequest,
    SemanticSearchResponse,
    StatsResponse,
)
from backend.src.modules.search.semantic_search_service import SemanticSearchService

logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(get_current_user)])

Neo4jSession = Annotated[Session, Depends(get_required_neo4j_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
EmbeddingService = Annotated[EmbeddingServiceType, Depends(get_embedding_service)]


@router.post(
    "/semantic", response_model=SemanticSearchResponse, summary="Semantic search"
)
def semanticSearchService(
    request: SemanticSearchRequest,
    embedding_service: EmbeddingService,
    neo4j: Neo4jSession,
    current_user: CurrentUser,
):
    service = SemanticSearchService(
        neo4j_session=neo4j, embedding_service=embedding_service
    )

    result = service._search(
        request.request_text, request.filter, request.limit_responses
    )
    return SemanticSearchResponse(results=result, total=len(result))


@router.get(
    "/impact-analysis/{node_id}",
    response_model=ImpactAnalysisResponse,
    summary="Get the problem consequence between the artifact",
)
def impact_analysis_search_service(
    node_id: str,
    neo4j: Neo4jSession,
    current_user: CurrentUser,
    depth: int = Query(default=5, gt=0, le=10),
):
    service = ImpactAnalysisService(neo4j_session=neo4j)

    try:
        result = service.get_impact(node_id, depth)
        return result
    except HTTPException:
        raise
    except (ValueError, TypeError) as e:
        logger.error(f"Invalid depth for impact analysis on node {node_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception(
            f"Unexpected error generating impact analysis for node {node_id}"
        )
        raise HTTPException(
            status_code=500, detail="Error occurred while generating impact analysis."
        )


@router.get(
    "/graph-stats", response_model=StatsResponse, summary="Get graph statistics"
)
def graph_stats_service(
    neo4j: Neo4jSession,
    current_user: CurrentUser,
):
    service = GraphService(neo4j_session=neo4j)
    result = service._get_graph_stats()
    return StatsResponse(**result)
