import json

import pydantic

from backend.src.modules.quality_intelligence.base_service import (
    QualityIntelligenceBaseService,
)
from backend.src.modules.quality_intelligence.health_score_service import (
    HealthScoreService,
)
from backend.src.modules.quality_intelligence.schemas import (
    RecommendationsResponse,
)


class RecommendationsService(QualityIntelligenceBaseService):
    def __init__(
        self, neo4j_session, ai_provider, health_score_service: HealthScoreService
    ):
        super().__init__(neo4j_session, ai_provider)
        self.health_score = health_score_service

    def _get_recommendation_evidence(self, node_id):
        """Fetch the health score data for a node from the graph database to use in recommendations service."""
        return self.health_score._fetch_health_score_data(node_id)

    def _build_recommendations_prompt(self, context) -> str:
        """Build a prompt string from a AI to generate typed recommendations."""
        prompt_parts = [
            f"context: {context}",
            "Above is the context of a specific artifact and its direct neighbors in the graph ",
            "(connected bugs, incidents, test cases, requirements).",
            "Based on this evidence, generate action recommendations to improve the quality ",
            "of this artifact. Each recommendation must use one of the following types, exactly as written:",
            "- EXECUTE_REGRESSION: when there are signs that a regression test suite should be run.",
            "- INCREASE_COVERAGE: when TestCases are missing to cover the artifact or its Requirements.",
            "- CREATE_TEST_CASE: when a specific scenario has no associated TestCase.",
            "- REVIEW_REQUIREMENT: when a Requirement seems ambiguous, outdated, or poorly covered.",
            "- PRIORITIZE_INTEGRATION: when there are signs that this artifact's integration with others should be prioritized.",
            "Respond strictly in JSON with:",
            "- recommendations (list of objects): each with 'type' (one of the 5 values above), ",
            "'priority' (Low/Medium/High) and 'justification' (required text, never empty, explaining ",
            "why this recommendation applies based on the context evidence).",
            "- ai_analysis (text): an overall summary of the analyzed artifact's quality state.",
        ]

        return "\n".join(prompt_parts)

    def get_ai_response(self, prompt) -> RecommendationsResponse:
        """Build a prompt string from a AI return the analysis of typed recommendation."""
        try:
            ai_response = self._call_llm(prompt)
            return RecommendationsResponse(
                recommendations=ai_response.get("recommendations", []),
                ai_analysis=ai_response.get("ai_analysis", ""),
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to decode AI response: {e}")
        except pydantic.ValidationError as e:
            raise ValueError(f"Failed because AI response is empty: {e}")

    def get_recommendations(self, node_id):
        """Retrieve the typed recommendation analysis"""
        recommendation = self._get_recommendation_evidence(node_id)

        if recommendation is None:
            return None

        context = self._build_health_score_context(
            recommendation.get("connected_nodes", {})
        )
        prompt = self._build_recommendations_prompt(context)
        return self.get_ai_response(prompt)
