from fastapi import APIRouter, Depends
from backend.src.core.dependencies import get_current_user, get_embedding_service
from backend.src.core.neo4j_db import get_neo4j_session
from backend.src.models.user import User
from backend.src.modules.search.schema import (
    SemanticSearchRequest,
    SemanticSearchResponse,
)
from backend.src.modules.search.semantic_search_service import SemanticSearchService

router = APIRouter()


@router.post(
    "/search/semantic", response_model=SemanticSearchResponse, summary="Semantic search"
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
    return result
