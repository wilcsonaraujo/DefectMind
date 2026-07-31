import json

from backend.src.modules.quality_intelligence.base_service import (
    QualityIntelligenceBaseService,
)
from backend.src.modules.quality_intelligence.schemas import (
    HotspotItem,
    HotspotsResponse,
)


class HotspotsService(QualityIntelligenceBaseService):

    def __init__(self, neo4j_session, ai_provider):
        super().__init__(neo4j_session, ai_provider)

    def _get_story_defect_counts(self, limit: int):
        """
        Retrieve stories with their associated defect counts and calculate a score.
        """
        query = """
        MATCH (s:Story)

        WITH s,
            COUNT { (s)-[:HAS_REQUIREMENT]->(:Requirement)-[:COVERED_BY]->(:TestCase)-[:FOUND]->(:BugReport) } AS bug_count,
            COUNT { (s)-[:HAS_REQUIREMENT]->(:Requirement)-[:COVERED_BY]->(:TestCase)-[:FOUND]->(b:BugReport)
                    WHERE b.severity = 'Critical' } AS critical_bug_count,
            COUNT { (s)-[:HAS_REQUIREMENT]->(:Requirement)-[:COVERED_BY]->(:TestCase)-[:FOUND]->(:BugReport)-[:CAUSED]->(:Incident) } AS incident_count,
            COUNT { (s)-[:HAS_REQUIREMENT]->(:Requirement)-[:COVERED_BY]->(:TestCase)-[:FOUND]->(:BugReport)-[:CAUSED]->(:Incident)-[:ROOT_CAUSE]->(:PostMortem) } AS postmortem_count

        WITH s,
            bug_count,
            critical_bug_count,
            incident_count,
            postmortem_count,
            (critical_bug_count * 3.0 +
            (bug_count - critical_bug_count) * 2.0 +
            incident_count * 2.0 +
            postmortem_count * 1.0) AS score

        WHERE score > 0

        RETURN
            s.id AS node_id,
            s.title AS title,
            'Story' AS label,
            bug_count,
            critical_bug_count,
            incident_count,
            postmortem_count,
            score
        ORDER BY score DESC, critical_bug_count DESC
        LIMIT $limit
        """
        return list(self.neo4j_session.run(query, limit=limit))

    def _build_hotspots_context(self, hotspots):
        """
        Build a context string from a list of hotspots.
        """
        context_parts = []
        for hotspot in hotspots:
            part = (
                f"[{hotspot.label}] title: {hotspot.title}\n"
                f"Bug Count: {hotspot.bug_count}\n"
                f"Critical Bug Count: {hotspot.critical_bug_count}\n"
                f"Incident Count: {hotspot.incident_count}\n"
                f"Postmortem Count: {hotspot.postmortem_count}\n"
                f"Score: {hotspot.score}"
            )
            context_parts.append(part)
        return "\n---\n".join(context_parts)

    def _build_hotspots_prompt(self, context):
        """Build a prompt string from a AI return the analysis of hotspots."""
        prompt_parts = [
            f"context: {context}",
            "Aqui está o ranking de Stories por concentração de defeitos, já ordenado do mais crítico para o menos crítico.",
            "Identifique padrões recorrentes entre as Stories mais problemáticas e responda estritamente em JSON com:",
            "ai_analysis (texto): análise dos padrões identificados",
            "recommendations (lista de strings): recomendações práticas e priorizadas",
        ]
        return "\n".join(prompt_parts)

    def get_ai_response(
        self, prompt: str, hotspots: list[HotspotItem]
    ) -> HotspotsResponse:
        """
        Get the AI response for the hotspots analysis.
        """
        try:
            ai_response = self._call_llm(prompt)
            return HotspotsResponse(
                hotspots=hotspots,
                total=len(hotspots),
                ai_analysis=ai_response.get("ai_analysis", ""),
                recommendations=ai_response.get("recommendations", []),
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to decode AI response: {e}")

    def get_hotspots(self, limit: int = 10) -> HotspotsResponse:
        """
        Retrieve the top hotspots based on defect counts.
        """
        records = self._get_story_defect_counts(limit=limit)

        hotspots = [
            HotspotItem(
                node_id=record["node_id"],
                title=record["title"],
                label=record["label"],
                bug_count=record["bug_count"],
                critical_bug_count=record["critical_bug_count"],
                incident_count=record["incident_count"],
                postmortem_count=record["postmortem_count"],
                score=record["score"],
            )
            for record in records
        ]

        if not hotspots:
            return HotspotsResponse(
                hotspots=[], total=0, ai_analysis="", recommendations=[]
            )

        context = self._build_hotspots_context(hotspots)
        prompt = self._build_hotspots_prompt(context)
        return self.get_ai_response(prompt, hotspots)
