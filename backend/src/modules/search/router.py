from fastapi import APIRouter, Depends, Query
from backend.src.core.dependencies import get_current_user, get_embedding_service
from backend.src.core.neo4j_db import get_neo4j_session
from backend.src.models.user import User
from backend.src.modules.search.impact_analysis_service import ImpactAnalysisService
from backend.src.modules.search.graph import GraphService
from backend.src.modules.search.schemas import (
    ImpactAnalysisResponse,
    SemanticSearchRequest,
    SemanticSearchResponse,
    StatsResponse,
)
from backend.src.modules.search.semantic_search_service import SemanticSearchService

router = APIRouter()


@router.post(
    "/semantic", response_model=SemanticSearchResponse, summary="Semantic search"
)
def semanticSearchService(
    request: SemanticSearchRequest,
    embedding_service=Depends(get_embedding_service),
    neo4j=Depends(get_neo4j_session),
    current_user: User = Depends(get_current_user),
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
    depth: int = Query(default=5, gt=0, le=10),
    neo4j=Depends(get_neo4j_session),
    current_user: User = Depends(get_current_user),
):
    service = ImpactAnalysisService(neo4j_session=neo4j)
    result = service.get_impact(node_id, depth)

    return result


@router.get("graph-stats", response_model=StatsResponse, summary="Get graph statistics")
def graph_stats_service(
    neo4j=Depends(get_neo4j_session), current_user: User = Depends(get_current_user)
):
    service = GraphService(neo4j_session=neo4j)
    total_nodes = service._get_total_nodes()
    total_edges = service._get_total_edges()
    nodes_by_type = service._get_nodes_by_type()
    most_connected_nodes = service._get_most_connected_nodes()

    return StatsResponse(
        total_nodes=total_nodes,
        total_edges=total_edges,
        nodes_by_type=nodes_by_type,
        most_connected_nodes=most_connected_nodes,
    )
