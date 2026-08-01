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
            "Acima está o contexto de um artefato específico e seus vizinhos diretos no grafo ",
            "(bugs, incidents, test cases, requirements conectados).",
            "Com base nessas evidências, gere recomendações de ação para melhorar a qualidade ",
            "desse artefato. Cada recomendação deve usar um dos seguintes tipos, exatamente como escrito:",
            "- EXECUTE_REGRESSION: quando há indícios de que uma bateria de testes de regressão deveria rodar.",
            "- INCREASE_COVERAGE: quando faltam TestCases cobrindo o artefato ou seus Requirements.",
            "- CREATE_TEST_CASE: quando um cenário específico não tem nenhum TestCase associado.",
            "- REVIEW_REQUIREMENT: quando um Requirement parece ambíguo, desatualizado ou mal coberto.",
            "- PRIORITIZE_INTEGRATION: quando há sinais de que a integração desse artefato com outros deveria ser priorizada.",
            "Responda estritamente em JSON com:",
            "- recommendations (lista de objetos): cada um com 'type' (um dos 5 valores acima), ",
            "'priority' (Low/Medium/High) e 'justification' (texto obrigatório, nunca vazio, explicando ",
            "por que essa recomendação se aplica com base nas evidências do contexto).",
            "- ai_analysis (texto): um resumo geral do estado de qualidade do artefato analisado.",
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
