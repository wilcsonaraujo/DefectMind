import json
from itertools import chain

from backend.src.modules.quality_intelligence.base_service import (
    QualityIntelligenceBaseService,
)
from backend.src.modules.quality_intelligence.schemas import (
    CoverageAnalysisResponse,
    CoverageGap,
)


class CoverageAnalysisService(QualityIntelligenceBaseService):
    def __init__(self, neo4j_session, ai_provider):
        super().__init__(neo4j_session, ai_provider)

    def _get_uncovered_requirements(self) -> list[CoverageGap]:
        """Searches for requirements that do not have any associated test cases."""
        query = """
        MATCH (r:Requirement)
        WHERE COUNT { (r)-[:COVERED_BY]->(:TestCase) } = 0
        RETURN
            r.id AS node_id,
            r.title AS title,
            'Requirement' AS label,
            'NO_TEST_CASE' AS gap_type
        """
        records = self.neo4j_session.run(query)

        return [
            CoverageGap(
                node_id=record["node_id"],
                title=record["title"],
                label=record["label"],
                gap_type=record["gap_type"],
            )
            for record in records
        ]

    def _get_uncovered_stories(self) -> list[CoverageGap]:
        """Search for stories that lack functional coverage (no associated test cases)."""
        query = """
        MATCH (s:Story)
        WHERE COUNT { (s)-[:HAS_REQUIREMENT]->(:Requirement)-[:COVERED_BY]->(:TestCase) } = 0
        RETURN
            s.id AS node_id,
            s.title AS title,
            'Story' AS label,
            'NO_FUNCTIONAL_COVERAGE' AS gap_type
        """
        records = self.neo4j_session.run(query)

        return [
            CoverageGap(
                node_id=record["node_id"],
                title=record["title"],
                label=record["label"],
                gap_type=record["gap_type"],
            )
            for record in records
        ]

    def _get_orphan_test_cases(self) -> list[CoverageGap]:
        """Searches for test cases that are not linked to any requirement."""
        query = """
        MATCH (tc:TestCase)
        WHERE COUNT { (:Requirement)-[:COVERED_BY]->(tc) } = 0
        RETURN
            tc.id AS node_id,
            tc.title AS title,
            'TestCase' AS label,
            'ORPHAN_TEST_CASE' AS gap_type
        """
        records = self.neo4j_session.run(query)

        return [
            CoverageGap(
                node_id=record["node_id"],
                title=record["title"],
                label=record["label"],
                gap_type=record["gap_type"],
            )
            for record in records
        ]

    def _compute_coverage_score(self) -> float:
        """Calculates the coverage score based solely on requirements."""

        query = """
        MATCH (r:Requirement)
        WITH r, COUNT { (r)-[:COVERED_BY]->(:TestCase) } = 0 AS is_uncovered
        RETURN
            COUNT(r) AS total_requirements,
            COUNT(CASE WHEN is_uncovered THEN 1 END) AS uncovered_requirements
        """

        result = self.neo4j_session.run(query)
        record = result.single()

        if not record:
            return 100.0

        total = record["total_requirements"]
        uncovered = record["uncovered_requirements"]

        if total == 0:
            return 100.0

        covered = total - uncovered
        return round((covered / total) * 100, 2)

    def _get_all_gaps_chain(self) -> list[CoverageGap]:
        """Unifies the three lists using itertools.chain."""
        return list(
            chain(
                self._get_uncovered_requirements(),
                self._get_uncovered_stories(),
                self._get_orphan_test_cases(),
            )
        )

    def _build_coverage_context(self, coverages):
        """Build a context string from a list of coverages."""

        context_parts = []
        for coverage in coverages:
            part = f"[{coverage.label} - {coverage.gap_type}] title: {coverage.title}"
            context_parts.append(part)
        return "\n---\n".join(context_parts)

    def _build_coverage_prompt(self, context, coverage_score):
        """Build a prompt string from a AI return the analysis of coverages."""
        prompt_parts = [
            f"context: {context}",
            f"Current coverage score: {coverage_score}/100 (percentage of Requirements with at least one linked TestCase).",
            "The gaps above are classified into three types:",
            "- NO_TEST_CASE: Requirement with no linked TestCase.",
            "- NO_FUNCTIONAL_COVERAGE: Story whose Requirements have no TestCase at all.",
            "- ORPHAN_TEST_CASE: TestCase that is not linked to any Requirement.",
            "Analyze these gaps and respond strictly in JSON with:",
            "- ai_analysis (text): a summary interpreting the overall coverage situation, highlighting the highest-risk areas and patterns among the gaps.",
            "- recommendations (list of strings): practical, prioritized actions to close the most critical gaps first.",
        ]
        return "\n".join(prompt_parts)

    def get_ai_response(
        self, prompt: str, gaps: list[CoverageGap], coverage_score: float
    ) -> CoverageAnalysisResponse:
        """
        Get the AI response for the coverage gap analysis.
        """
        try:
            ai_response = self._call_llm(prompt)
            return CoverageAnalysisResponse(
                coverage_score=coverage_score,
                gaps=gaps,
                ai_analysis=ai_response.get("ai_analysis", ""),
                recommendations=ai_response.get("recommendations", []),
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to decode AI response: {e}")

    def get_coverage_analysis(self) -> CoverageAnalysisResponse:
        """
        Retrieve the coverage gap based in requirements and test cases.
        """
        records = self._get_all_gaps_chain()

        if not records:
            return CoverageAnalysisResponse(
                coverage_score=100.0,
                gaps=[],
                ai_analysis="",
                recommendations=[],
            )

        context = self._build_coverage_context(records)
        coverage_score = self._compute_coverage_score()
        prompt = self._build_coverage_prompt(context, coverage_score)
        return self.get_ai_response(prompt, records, coverage_score)
