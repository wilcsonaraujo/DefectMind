from backend.src.modules.quality_intelligence.base_service import (
    QualityIntelligenceBaseService,
)
from backend.src.modules.search.semantic_search_service import SemanticSearchService


class ReleaseReadinessService(QualityIntelligenceBaseService):
    def __init__(
        self, neo4j_session, ai_provider, semantic_search_service: SemanticSearchService
    ):
        super().__init__(neo4j_session, ai_provider)
        self.semantic_search = semantic_search_service

    def _get_direct_risk_evidence(self, node_id) -> list[dict]:
        """Searches for noisy neighbors (BugReport and Incident) starting from a node."""

        query = """
        MATCH (main {id: $node_id})
        OPTIONAL MATCH (main)-[]-(connected)
        WHERE connected:BugReport OR connected:Incident
        RETURN
            connected.id AS node_id,
            connected.title AS title,
            labels(connected)[0] AS label,
            connected.severity AS severity,
            connected.impact AS impact
        """
        results = list(self.neo4j_session.run(query, node_id=node_id))

        if not results:
            return []

        return [
            dict(
                node_id=result["node_id"],
                title=result["title"],
                label=result["label"],
                severity=result["severity"],
                impact=result["impact"],
            )
            for result in results
        ]

    def _get_semantic_risk_evidence(self, node_id) -> list[dict]:
        """Searches for artifacts with a similar description that have a history of problems."""

        query = """
        MATCH (main {id: $node_id}) 
        RETURN main.title AS title
        """
        title = self.neo4j_session.run(query, node_id=node_id).single()["title"]
        labels = ["BugReport", "Incident", "PostMortem"]

        result = []
        for label in labels:
            matches = self.semantic_search._search(
                request_text=title, filter=label, limit=3
            )
            for match in matches:
                if match.id == node_id:
                    continue
                result.append({
                    "node_id": match.id,
                    "title": match.title,
                    "label": match.label,
                    "score": match.score
                })

        return result

    def _build_risk_report_context(self, direct_evidence, semantic_evidence):
        """Builds a labeled context string combining structural and semantic risk evidence."""
        parts = []
        for item in direct_evidence:
            risk_indicator = item["severity"] or item["impact"]
            parts.append(
                f"[Estrutural] {item['label']} '{item['title']}' "
                f"(severity: {risk_indicator}) — conectado diretamente ao artefato analisado."
            )

        for item in semantic_evidence:
            parts.append(
                f"[Semântico] {item['label']} '{item['title']}' "
                f"(similaridade: {item['score']:.2f}) — encontrado por busca de artefatos parecidos."
            )

        return "\n".join(parts)

        



