from datetime import datetime, timezone
import uuid

from fastapi import APIRouter, Depends, HTTPException
from backend.src.core.dependencies import get_current_user
from backend.src.core.neo4j_db import get_neo4j_session
from backend.src.models.user import User
from backend.src.modules.artifacts.schemas import (
    BugReportRequest,
    BugReportResponse,
    IncidentRequest,
    IncidentResponse,
    PostMortemRequest,
    PostMortemResponse,
    RelationshipRequest,
    RequirementRequest,
    RequirementResponse,
    StoryRequest,
    StoryResponse,
    TestCaseRequest,
    TestCaseResponse,
)

router = APIRouter()


@router.get(
    "/stories", response_model=list[StoryResponse], summary="Get all stories from Neo4j"
)
def get_stories(
    neo4j=Depends(get_neo4j_session), current_user: User = Depends(get_current_user)
):

    query = """MATCH (s:Story) RETURN s"""
    result = neo4j.run(query)
    stories = [dict(record["s"]) for record in result]

    if not stories:
        return []

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

    query = """MATCH (s:Story {id: $story_id}) RETURN s"""
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

    query = """CREATE (s:Story {id: $id, title: $title, description: $description, created_at: $created_at}) RETURN s"""
    result = neo4j.run(
        query,
        id=new_id,
        title=story.title,
        description=story.description,
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

    query = """MATCH (r:Requirement) RETURN r"""
    result = neo4j.run(query)
    requirements = [dict(record["r"]) for record in result]

    if not requirements:
        return []

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
    query = """CREATE (r:Requirement {id: $id, description: $description, priority: $priority, created_at: $created_at}) RETURN r"""
    result = neo4j.run(
        query,
        id=new_id,
        description=requirement.description,
        priority=requirement.priority,
        created_at=created_at,
    )
    created_requirement = [dict(record["r"]) for record in result]

    return created_requirement[0] if created_requirement else None


@router.get(
    "/testcases",
    response_model=list[TestCaseResponse],
    summary="Get all test cases from Neo4j",
)
def get_test_cases(
    neo4j=Depends(get_neo4j_session), current_user: User = Depends(get_current_user)
):
    query = """MATCH (t:TestCase) RETURN t"""
    result = neo4j.run(query)
    test_cases = [dict(record["t"]) for record in result]

    if not test_cases:
        return []

    return test_cases


@router.post(
    "/testcases",
    response_model=TestCaseResponse,
    summary="Create a new test case in Neo4j",
)
def create_test_case(
    test_case: TestCaseRequest,
    neo4j=Depends(get_neo4j_session),
    current_user: User = Depends(get_current_user),
):
    new_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    query = """CREATE (t:TestCase {id: $id, title: $title, steps: $steps, expected_result: $expected_result, created_at: $created_at}) RETURN t"""
    result = neo4j.run(
        query,
        id=new_id,
        title=test_case.title,
        steps=test_case.steps,
        expected_result=test_case.expected_result,
        created_at=created_at,
    )
    created_test_case = [dict(record["t"]) for record in result]

    return created_test_case[0] if created_test_case else None


@router.get(
    "/bugreports",
    response_model=list[BugReportResponse],
    summary="Get all bug reports from Neo4j",
)
def get_bug_reports(
    neo4j=Depends(get_neo4j_session), current_user: User = Depends(get_current_user)
):
    query = """MATCH (b:BugReport) RETURN b"""
    result = neo4j.run(query)
    bug_reports = [dict(record["b"]) for record in result]

    if not bug_reports:
        return []

    return bug_reports


@router.post(
    "/bugreports",
    response_model=BugReportResponse,
    summary="Create a new bug report in Neo4j",
)
def create_bug_report(
    bug_report: BugReportRequest,
    neo4j=Depends(get_neo4j_session),
    current_user: User = Depends(get_current_user),
):
    new_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    query = """CREATE (b:BugReport {id: $id, title: $title, description: $description, severity: $severity, created_at: $created_at}) RETURN b"""
    result = neo4j.run(
        query,
        id=new_id,
        title=bug_report.title,
        description=bug_report.description,
        severity=bug_report.severity,
        created_at=created_at,
    )
    created_bug_report = [dict(record["b"]) for record in result]

    return created_bug_report[0] if created_bug_report else None


@router.get(
    "/incidents",
    response_model=list[IncidentResponse],
    summary="Get all incidents from Neo4j",
)
def get_incidents(
    neo4j=Depends(get_neo4j_session), current_user: User = Depends(get_current_user)
):
    query = """MATCH (i:Incident) RETURN i"""
    result = neo4j.run(query)
    incidents = [dict(record["i"]) for record in result]

    if not incidents:
        return []

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
    query = """CREATE (i:Incident {id: $id, title: $title, description: $description, impact: $impact, created_at: $created_at}) RETURN i"""
    result = neo4j.run(
        query,
        id=new_id,
        title=incident.title,
        description=incident.description,
        impact=incident.impact.value,
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
    query = """MATCH (p:PostMortem) RETURN p"""
    result = neo4j.run(query)
    postmortems = [dict(record["p"]) for record in result]

    if not postmortems:
        return []

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
    query = """CREATE (p:PostMortem {id: $id, root_cause: $root_cause, resolution: $resolution, lessons_learned: $lessons_learned, created_at: $created_at}) RETURN p"""
    result = neo4j.run(
        query,
        id=new_id,
        root_cause=postmortem.root_cause,
        resolution=postmortem.resolution,
        lessons_learned=postmortem.lessons_learned,
        created_at=created_at,
    )
    created_postmortem = [dict(record["p"]) for record in result]

    return created_postmortem[0] if created_postmortem else None


@router.post(
    "/stories/{story_id}/requirements/{req_id}", summary="Link a requirement to a story"
)
def link_requirement_to_story(
    story_id: str,
    req_id: str,
    neo4j=Depends(get_neo4j_session),
    current_user: User = Depends(get_current_user),
):
    query = """
    MATCH (s:Story {id: $story_id}), (r:Requirement {id: $req_id})
    MERGE (s)-[rel:HAS_REQUIREMENT]->(r)
    RETURN s, r, rel
    """
    result = neo4j.run(
        query,
        story_id=story_id,
        req_id=req_id,
    )
    records = [dict(record) for record in result]

    if not records:
        raise HTTPException(
            status_code=404, detail="Story or Requirement ID not found."
        )

    return {"message": "Requirement linked to Story successfully."}


@router.post(
    "/requirements/{req_id}/testcases/{tc_id}",
    summary="Link a test case to a requirement",
)
def link_testcase_to_requirement(
    req_id: str,
    tc_id: str,
    neo4j=Depends(get_neo4j_session),
    current_user: User = Depends(get_current_user),
):
    query = """
    MATCH (r:Requirement {id: $req_id}), (t:TestCase {id: $tc_id})
    MERGE (r)-[rel:COVERED_BY]->(t)
    RETURN r, t, rel
    """
    result = neo4j.run(
        query,
        req_id=req_id,
        tc_id=tc_id,
    )
    records = [dict(record) for record in result]

    if not records:
        raise HTTPException(
            status_code=404, detail="Requirement or Test Case ID not found."
        )

    return {"message": "Test Case linked to Requirement successfully."}

@router.post(
    "/testcases/{tc_id}/bugs/{bug_id}",
    summary="Link a test case to a bug",
)
def link_testcase_to_bug(
    tc_id: str,
    bug_id: str,
    neo4j=Depends(get_neo4j_session),
    current_user: User = Depends(get_current_user),
):
    query = """
    MATCH (t:TestCase {id: $tc_id}), (b:BugReport {id: $bug_id})
    MERGE (t)-[rel:FOUND]->(b)
    RETURN t, b, rel
    """
    result = neo4j.run(
        query,
        tc_id=tc_id,
        bug_id=bug_id,
    )
    records = [dict(record) for record in result]

    if not records:
        raise HTTPException(
            status_code=404, detail="Test Case or Bug ID not found."
        )

    return {"message": "Test Case linked to Bug successfully."}


@router.post(
    "/bugs/{bug_id}/incidents/{incident_id}",
    summary="Link a bug to an incident",
)
def link_bug_to_incident(
    bug_id: str,
    incident_id: str,
    neo4j=Depends(get_neo4j_session),
    current_user: User = Depends(get_current_user),
):
    query = """
    MATCH (b:BugReport {id: $bug_id}), (i:Incident {id: $incident_id})
    MERGE (b)-[rel:CAUSED]->(i)
    RETURN b, i, rel
    """
    result = neo4j.run(
        query,
        bug_id=bug_id,
        incident_id=incident_id,
    )
    records = [dict(record) for record in result]

    if not records:
        raise HTTPException(status_code=404, detail="Bug or Incident ID not found.")

    return {"message": "Incident linked to Bug successfully."}


@router.post(
    "/incidents/{incident_id}/postmortems/{pm_id}",
    summary="Link an incident to a postmortem",
)
def link_incident_to_postmortem(
    incident_id: str,
    pm_id: str,
    neo4j=Depends(get_neo4j_session),
    current_user: User = Depends(get_current_user),
):
    query = """
    MATCH (i:Incident {id: $incident_id}), (p:PostMortem {id: $pm_id})
    MERGE (i)-[rel:ROOT_CAUSE]->(p)
    RETURN i, p, rel
    """
    result = neo4j.run(
        query,
        pm_id=pm_id,
        incident_id=incident_id,
    )
    records = [dict(record) for record in result]

    if not records:
        raise HTTPException(
            status_code=404, detail="Incident or PostMortem ID not found."
        )

    return {"message": "Incident linked to PostMortem successfully."}
