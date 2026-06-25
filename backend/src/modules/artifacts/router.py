from datetime import datetime, timezone
import uuid

from fastapi import APIRouter, Depends, HTTPException
from backend.src.core.dependencies import get_current_user
from backend.src.core.neo4j_db import get_neo4j_session
from backend.src.models.user import User
from backend.src.modules.artifacts.schemas import (
    IncidentRequest,
    IncidentResponse,
    PostMortemRequest,
    PostMortemResponse,
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

    if not stories:
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
    stories = [dict(record["s"]) for record in result]

    if not stories:
        raise HTTPException(status_code=404, detail="Story ID not found.")

    return stories[0]


@router.post(
    "/stories", response_model=StoryResponse, summary="Create a new story in Neo4j"
)
def create_story(
    story: StoryRequest,
    neo4j=Depends(get_neo4j_session),
    current_user: User = Depends(get_current_user),
):
    new_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()

    query = "CREATE (s:Story {id: $id, title: $title, content: $content, created_at: $created_at}) RETURN s"
    result = neo4j.run(
        query,
        id=new_id,
        title=story.title,
        content=story.content,
        created_at=created_at,
    )
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

    if not requirements:
        raise HTTPException(status_code=404, detail="No requirements found.")

    return requirements


@router.post(
    "/requirements",
    response_model=RequirementResponse,
    summary="Create a new requirement in Neo4j",
)
def create_requirement(
    requirement: RequirementRequest,
    neo4j=Depends(get_neo4j_session),
    current_user: User = Depends(get_current_user),
):
    new_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    query = "CREATE (r:Requirement {id: $id, title: $title, description: $description, created_at: $created_at}) RETURN r"
    result = neo4j.run(
        query,
        id=new_id,
        title=requirement.title,
        description=requirement.description,
        created_at=created_at,
    )
    created_requirement = [dict(record["r"]) for record in result]

    return created_requirement[0] if created_requirement else None


@router.get(
    "/incidents",
    response_model=list[IncidentResponse],
    summary="Get all incidents from Neo4j",
)
def get_incidents(
    neo4j=Depends(get_neo4j_session), current_user: User = Depends(get_current_user)
):
    query = "MATCH (i:Incident) RETURN i"
    result = neo4j.run(query)
    incidents = [dict(record["i"]) for record in result]

    if not incidents:
        raise HTTPException(status_code=404, detail="No incidents found.")

    return incidents


@router.post(
    "/incidents",
    response_model=IncidentResponse,
    summary="Create a new incident in Neo4j",
)
def create_incident(
    incident: IncidentRequest,
    neo4j=Depends(get_neo4j_session),
    current_user: User = Depends(get_current_user),
):
    new_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    query = "CREATE (i:Incident {id: $id, title: $title, description: $description, created_at: $created_at}) RETURN i"
    result = neo4j.run(
        query,
        id=new_id,
        title=incident.title,
        description=incident.description,
        created_at=created_at,
    )
    created_incident = [dict(record["i"]) for record in result]

    return created_incident[0] if created_incident else None


@router.get(
    "/postmortems",
    response_model=list[PostMortemResponse],
    summary="Get all post-mortems from Neo4j",
)
def get_postmortems(
    neo4j=Depends(get_neo4j_session), current_user: User = Depends(get_current_user)
):
    query = "MATCH (p:PostMortem) RETURN p"
    result = neo4j.run(query)
    postmortems = [dict(record["p"]) for record in result]

    if not postmortems:
        raise HTTPException(status_code=404, detail="No post-mortems found.")

    return postmortems


@router.post(
    "/postmortems",
    response_model=PostMortemResponse,
    summary="Create a new post-mortem in Neo4j",
)
def create_postmortem(
    postmortem: PostMortemRequest,
    neo4j=Depends(get_neo4j_session),
    current_user: User = Depends(get_current_user),
):
    new_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    query = "CREATE (p:PostMortem {id: $id, title: $title, description: $description, created_at: $created_at}) RETURN p"
    result = neo4j.run(
        query,
        id=new_id,
        title=postmortem.title,
        description=postmortem.description,
        created_at=created_at,
    )
    created_postmortem = [dict(record["p"]) for record in result]

    return created_postmortem[0] if created_postmortem else None
