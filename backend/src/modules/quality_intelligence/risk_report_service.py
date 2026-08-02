import json

from backend.src.modules.quality_intelligence.base_service import (
    QualityIntelligenceBaseService,
)
from backend.src.modules.quality_intelligence.schemas import RiskReportResponse
from backend.src.modules.search.semantic_search_service import SemanticSearchService


class RiskReportService(QualityIntelligenceBaseService):
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
            {
                "node_id": result["node_id"],
                "title": result["title"],
                "label": result["label"],
                "severity": result["severity"],
                "impact": result["impact"],
            }
            for result in results
            if result["node_id"] is not None
        ]

    def _get_semantic_risk_evidence(self, node_id, title) -> list[dict]:
        """Searches for artifacts with a similar description that have a history of problems."""
        labels = ["BugReport", "Incident", "PostMortem"]

        result = []
        for label in labels:
            matches = self.semantic_search._search(
                request_text=title, filter=label, limit=3
            )
            for match in matches:
                if match.id == node_id:
                    continue
                result.append(
                    {
                        "node_id": match.id,
                        "title": match.properties.get("title"),
                        "label": match.label,
                        "score": match.score,
                    }
                )

        return result

    def _build_risk_report_context(self, direct_evidence, semantic_evidence):
        """Builds a labeled context string combining structural and semantic risk evidence."""
        parts = []
        for item in direct_evidence:
            risk_indicator = item["severity"] or item["impact"]
            parts.append(
                f"[Structural] {item['label']} '{item['title']}' "
                f"(severity: {risk_indicator}) — connected directly to the analyzed artifact."
            )

        for item in semantic_evidence:
            parts.append(
                f"[Semantic] {item['label']} '{item['title']}' "
                f"(similaridade: {item['score']:.2f}) — found by searching for similar artifacts."
            )

        return "\n".join(parts)

    def _build_risk_report_prompt(self, context):
        """Build a prompt string from a AI to synthesize a risk report."""
        prompt_parts = [
            f"context: {context}",
            "Above is a list of risk evidence for a specific artifact, ",
            "found in two ways: [Structural] (direct connections in the graph with the artifact) ",
            "and [Semantic] (search for artifacts with a similar title and history of problems).",
            "Analyze this evidence and respond strictly in JSON with:",
            "- risks (list of objects): each with 'artifact' (name/title of the cited artifact), ",
            "'type' (indicate whether the evidence is 'structural' or 'semantic', citing the source), ",
            "and 'justification' (why this artifact represents a risk to the artifact being analyzed).",
            "- ai_analysis (text): a summary of the artifact's overall risk level, based on the set of evidence.",
            "- recommendations (list of strings): practical actions to mitigate the identified risks.",
        ]
        return "\n".join(prompt_parts)

    def get_ai_response(self, prompt) -> RiskReportResponse:
        """Build a prompt string from a AI return the analysis of risk report."""
        try:
            ai_response = self._call_llm(prompt)
            return RiskReportResponse(
                risks=ai_response.get("risks", []),
                ai_analysis=ai_response.get("ai_analysis", ""),
                recommendations=ai_response.get("recommendations", []),
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to decode AI response: {e}")

    def get_risk_report(self, node_id) -> RiskReportResponse:
        """Retrieve the risk report analysis"""
        query = """
        MATCH (main {id: $node_id})
        RETURN main.title AS title
        """
        record = self.neo4j_session.run(query, node_id=node_id).single()

        if record is None:
            return None

        title = record["title"]

        evidence_risks_list = self._get_direct_risk_evidence(node_id)
        semantic_risk_list = self._get_semantic_risk_evidence(node_id, title)

        if not semantic_risk_list and not evidence_risks_list:
            return RiskReportResponse(
                risks=[], ai_analysis="Nenhum risco identificado.", recommendations=[]
            )

        context = self._build_risk_report_context(
            evidence_risks_list, semantic_risk_list
        )
        prompt = self._build_risk_report_prompt(context)
        return self.get_ai_response(prompt)
