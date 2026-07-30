import json

from backend.src.modules.quality_intelligence.base_service import (
    QualityIntelligenceBaseService,
)
from backend.src.modules.quality_intelligence.schemas import (
    ReleaseReadinessResponse,
    RiskLevelEnum,
    StoryReadiness,
)


class ReleaseReadinessService(QualityIntelligenceBaseService):
    def __init__(self, neo4j_session, ai_provider):
        super().__init__(neo4j_session, ai_provider)

    def _validate_story_ids(self, story_ids) -> list:
        """Validate the stories ID's and delivery the ID's that don't exist"""
        query = """
            MATCH (s:Story) 
            WHERE s.id IN $story_ids 
            RETURN s.id AS found_id
            """

        records = self.neo4j_session.run(query, story_ids=story_ids)
        found_ids = [record["found_id"] for record in records]

        return list(set(story_ids) - set(found_ids))

    def _get_story_coverage(self, story_id) -> float:
        """Calculates the coverage score based solely on stories."""
        query = """
        MATCH (s:Story {id: $story_id})-[:HAS_REQUIREMENT]->(r:Requirement)
        WITH r, COUNT { (r)-[:COVERED_BY]->(:TestCase) } = 0 AS is_uncovered
        RETURN
            COUNT(r) AS total_requirements,
            COUNT(CASE WHEN is_uncovered THEN 1 END) AS uncovered_requirements
        """
        record = self.neo4j_session.run(query, story_id=story_id).single()

        if not record:
            return 100.0

        total = record["total_requirements"]
        uncovered = record["uncovered_requirements"]

        if total == 0:
            return 100.0

        covered = total - uncovered
        return round((covered / total) * 100, 2)

    def _get_story_health_signal(self, story_id):
        """Calculates the health signal of a Story."""
        query = """
        MATCH (s:Story {id: $story_id})
        OPTIONAL MATCH (s)-[]-(connected)
        RETURN
            COUNT(CASE WHEN connected:BugReport THEN 1 END) AS bug_report_count,
            COUNT(CASE WHEN connected:Incident THEN 1 END) AS incident_count,
            COUNT(CASE WHEN connected:PostMortem THEN 1 END) AS postmortem_count
        """
        result = self.neo4j_session.run(query, story_id=story_id).single()

        if not result:
            return None

        bug_report_count = result["bug_report_count"]
        incident_count = result["incident_count"]
        postmortem_count = result["postmortem_count"]

        severity_score = (
            bug_report_count * 2 + incident_count * 3 + postmortem_count * 4
        )

        if severity_score >= 15:
            return RiskLevelEnum.HIGH.value
        elif severity_score >= 5:
            return RiskLevelEnum.MEDIUM.value
        else:
            return RiskLevelEnum.LOW.value

    def _get_story_incidents_without_postmortem(self, story_id) -> int:
        """Counts how many incidents in the story's path do not have an associated post-mortem."""
        query = """
        MATCH (s:Story {id: $story_id})
            MATCH (s)-[:HAS_REQUIREMENT]->(:Requirement)-[:COVERED_BY]->(:TestCase)-[:FOUND]->(:BugReport)-[:CAUSED]->(i:Incident)
            WHERE COUNT { (i)-[:ROOT_CAUSE]->(:PostMortem) } = 0
            RETURN COUNT(DISTINCT i) AS incidents_without_postmortem
        """

        result = self.neo4j_session.run(query, story_id=story_id).single()

        if not result:
            return 0

        return result["incidents_without_postmortem"]

    def _compute_verdict(self, coverage_score, health_risk, incidents_count) -> dict:
        """Calculates the verdict and the list of deployment blockers"""

        blockers = []
        if coverage_score < 50 or health_risk == "HIGH":
            verdict = "NOT_READY"

            if coverage_score < 50:
                blockers.append(
                    f"cobertura de testes em {coverage_score:.1f}% (mínimo 50%)"
                )
            if health_risk == "HIGH":
                blockers.append("health score classificado como HIGH")

        elif (
            (50 <= coverage_score < 80)
            or health_risk == "MEDIUM"
            or incidents_count > 0
        ):
            verdict = "NEEDS_ATTENTION"

            if 50 <= coverage_score < 80:
                blockers.append(
                    f"cobertura de testes em {coverage_score:.1f}% (ideal > 80%)"
                )
            if health_risk == "MEDIUM":
                blockers.append("health score classificado como MEDIUM")
            if incidents_count > 0:
                blockers.append(f"{incidents_count} incidente(s) sem postmortem")

        else:
            verdict = "READY"

        return {"verdict": verdict, "blockers": blockers}

    def _assess_story(self, story_id) -> StoryReadiness:
        """Orchestrates the coverage_score, health_risk and incidents_count methods and returns a StoryReadiness object."""

        query = """MATCH (s:Story {id: $story_id}) RETURN s.title AS title"""
        title = self.neo4j_session.run(query, story_id=story_id).single()["title"]

        coverage_score = self._get_story_coverage(story_id)
        health_risk = self._get_story_health_signal(story_id)
        incidents_count = self._get_story_incidents_without_postmortem(story_id)

        result = self._compute_verdict(coverage_score, health_risk, incidents_count)

        return StoryReadiness(
            story_id=story_id,
            title=title,
            verdict=result["verdict"],
            incidents_count=incidents_count,
            coverage_score=coverage_score,
            health_risk=health_risk,
            blockers=result["blockers"],
        )

    def _build_release_readiness_context(self, results):
        """Build a context string from a release readiness"""
        context_parts = []
        for result in results:
            part = (
                f"Title: {result.title}\n"
                f"Verdict: {result.verdict}\n"
                f"Incidents without postmortem count: {result.incidents_count}\n"
                f"Coverage score: {result.coverage_score}\n"
                f"Health risk: {result.health_risk}\n"
                f"Blockers: {result.blockers}"
            )
            context_parts.append(part)
        return "\n---\n".join(context_parts)

    def _build_release_readiness_prompt(self, context):
        """Build a prompt string from a AI return the analysis of release readiness."""
        prompt_parts = [
            f"context: {context}",
            "Acima está a avaliação de prontidão de cada Story pra release, com verdict (READY/NEEDS_ATTENTION/NOT_READY), cobertura de testes, risco de saúde (health_risk) e incidents sem postmortem.",
            "Analise o conjunto e responda estritamente em JSON com:",
            "- ai_analysis (texto): um resumo do risco geral do lote de Stories, destacando quais estão mais longe de ficar prontas e por quê.",
            "- recommendations (lista de strings): ações práticas e priorizadas pra destravar as Stories NOT_READY/NEEDS_ATTENTION primeiro.",
        ]
        return "\n".join(prompt_parts)

    def get_ai_response(self, prompt, results) -> ReleaseReadinessResponse:
        """Get the AI response for the release readiness analysis."""
        try:
            ai_response = self._call_llm(prompt)
            return ReleaseReadinessResponse(
                results=results,
                ai_analysis=ai_response.get("ai_analysis", ""),
                recommendations=ai_response.get("recommendations", []),
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to decode AI response: {e}")

    def get_release_readiness(self, story_ids) -> ReleaseReadinessResponse:
        """Retrieve the release readiness analysis"""
        missing_ids = self._validate_story_ids(story_ids)
        if missing_ids:
            raise StoryNotFoundError(missing_ids)

        results = [self._assess_story(story_id) for story_id in story_ids]
        context = self._build_release_readiness_context(results)
        prompt = self._build_release_readiness_prompt(context)
        return self.get_ai_response(prompt, results)


class StoryNotFoundError(Exception):
    """Raised when one or more requested story_ids don't exist in the graph."""

    def __init__(self, missing_ids: list[str]):
        self.missing_ids = missing_ids
        super().__init__(f"Story(ies) not found: {missing_ids}")
