from fastapi import APIRouter, Depends, HTTPException
from backend.src.core.dependencies import get_current_user
from backend.src.core.neo4j_db import get_neo4j_session
from backend.src.models.user import User
from backend.src.modules.artifacts.schemas import (
    RequirementRequest,
    RequirementResponse,
    StoryRequest,
    StoryResponse,
)

router = APIRouter()


@router.get(
    "/stories", response_model=list[StoryResponse], summary="Get all stories from Neo4j"
)
def get_stories(
    neo4j=Depends(get_neo4j_session), current_user: User = Depends(get_current_user)
):

    query = "MATCH (s:Story) RETURN s"
    result = neo4j.run(query)
    stories = [dict(record["s"]) for record in result]

    if result is None:
        raise HTTPException(status_code=404, detail="No stories found.")

    return stories


@router.get(
    "/stories/{story_id}",
    response_model=list[StoryResponse],
    summary="Get story by ID from Neo4j",
)
def get_stories_id(
    story_id: str,
    neo4j=Depends(get_neo4j_session),
    current_user: User = Depends(get_current_user),
):

    query = "MATCH (s:Story {id: $story_id}) RETURN s"
    result = neo4j.run(query, story_id=story_id)

    if result is None:
        raise HTTPException(status_code=404, detail="Story ID not found.")

    stories = [dict(record["s"]) for record in result]
    return stories


@router.post(
    "/stories", response_model=StoryRequest, summary="Create a new story in Neo4j"
)
def create_story(
    story: StoryRequest,
    neo4j=Depends(get_neo4j_session),
    current_user: User = Depends(get_current_user),
):

    query = "CREATE (s:Story {title: $title, content: $content}) RETURN s"
    result = neo4j.run(query, title=story.title, content=story.content)
    created_story = [dict(record["s"]) for record in result]

    return created_story[0] if created_story else None


@router.get(
    "/requirements",
    response_model=list[RequirementResponse],
    summary="Get all requirements from Neo4j",
)
def get_requirements(
    neo4j=Depends(get_neo4j_session), current_user: User = Depends(get_current_user)
):

    query = "MATCH (r:Requirement) RETURN r"
    result = neo4j.run(query)
    requirements = [dict(record["r"]) for record in result]

    if result is None:
        raise HTTPException(status_code=404, detail="No requirements found.")

    return requirements


@router.post(
    "/requirements",
    response_model=RequirementRequest,
    summary="Create a new requirement in Neo4j",
)
def create_requirement(
    requirement: RequirementRequest,
    neo4j=Depends(get_neo4j_session),
    current_user: User = Depends(get_current_user),
):

    query = "CREATE (r:Requirement {title: $title, description: $description}) RETURN r"
    result = neo4j.run(
        query, title=requirement.title, description=requirement.description
    )
    created_requirement = [dict(record["r"]) for record in result]

    return created_requirement[0] if created_requirement else None
