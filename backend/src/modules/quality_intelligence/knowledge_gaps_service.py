from itertools import chain
import json

from backend.src.modules.quality_intelligence.base_service import (
    QualityIntelligenceBaseService,
)
from backend.src.modules.quality_intelligence.schemas import KnowledgeGap, KnowledgeGapsResponse

class KnowledgeGapsService(QualityIntelligenceBaseService):
    def __init__(self, neo4j_session, ai_provider):
        super().__init__(neo4j_session, ai_provider)

    def _get_bugs_without_test_case(self) -> list[KnowledgeGap]:
        """Searches for bugs that do not have any associated test cases"""
        query = """
        MATCH (b:BugReport)
        WHERE COUNT { (b)-[:FOUND_BY]->(:TestCase) } = 0
        RETURN
            b.id AS node_id,
            b.title AS title,
            'BugReport' AS label,
            'BUG_WITHOUT_TEST_CASE' AS gap_type
        """

        records = self.db_session.run(query)
        return [
            KnowledgeGap(
                node_id=record["node_id"],
                title=record["title"],
                label=record["label"],
                gap_type=record["gap_type"],
            )
            for record in records
        ]

    def _get_incidents_without_postmortem(self) -> list[KnowledgeGap]:
        """Searches for incidents that do not have any associated postmortem"""
        query = """
        MATCH (i:Incident)
        WHERE COUNT { (i)-[:ROOT_CAUSE]->(:PostMortem) } = 0
        RETURN
            i.id AS node_id,
            i.title AS title,
            'Incident' AS label,
            'NO_POSTMORTEM' AS gap_type
        """

        records = self.db_session.run(query)
        return [
            KnowledgeGap(
                node_id=record["node_id"],
                title=record["title"],
                label=record["label"],
                gap_type=record["gap_type"],
            )
            for record in records
        ]

    def _get_requirements_without_story(self) -> list[KnowledgeGap]:
        """Searches for requirements that do not have any associated story"""
        query = """
        MATCH (r:Requirement)
        WHERE COUNT { (:Story)-[:HAS_REQUIREMENT]->(r) } = 0
        RETURN
            r.id AS node_id,
            r.title AS title,
            'Requirement' AS label,
            'NO_STORY' AS gap_type
        """

        records = self.db_session.run(query)
        return [
            KnowledgeGap(
                node_id=record["node_id"],
                title=record["title"],
                label=record["label"],
                gap_type=record["gap_type"],
            )
            for record in records
        ]

    def _get_stories_without_requirements(self) -> list[KnowledgeGap]:
        """Searches for stories that do not have any associated requirements"""
        query = """
        MATCH (s:Story)
        WHERE COUNT { (s)-[:HAS_REQUIREMENT]->(:Requirement) } = 0
        RETURN
            s.id AS node_id,
            s.title AS title,
            'Story' AS label,
            'NO_REQUIREMENTS' AS gap_type
        """

        records = self.db_session.run(query)
        return [
            KnowledgeGap(
                node_id=record["node_id"],
                title=record["title"],
                label=record["label"],
                gap_type=record["gap_type"],
            )
            for record in records
        ]

    def _get_all_gaps_chain(self) -> list[KnowledgeGap]:
        """Unifies the three lists using itertools.chain."""
        return list(chain(
            self._get_bugs_without_test_case(),
            self._get_incidents_without_postmortem(),
            self._get_requirements_without_story(),
            self._get_stories_without_requirements()
        ))

    def _build_knowledge_gaps_context(self, knowledges):
        """Build a context string from a list of knowledges"""
        context_parts = []
        for knowledge in knowledges:
            part = (f"[{knowledge.label} - {knowledge.gap_type}] title: {knowledge.title}")
            context_parts.append(part)
        return "\n---\n".join(context_parts)

    def _build_knowledge_gaps_prompt(self, context):
        """Build a prompt string from a AI return the analysis of coverages."""
        prompt_parts = [
            f"context: {context}",
            "As inconsistências acima representam falhas de rastreabilidade no processo de QA, classificadas em quatro tipos:",
            "- BUG_WITHOUT_TEST_CASE: BugReport que não foi encontrado por nenhum TestCase registrado.",
            "- INCIDENT_WITHOUT_POSTMORTEM: Incident sem nenhuma análise de causa raiz (PostMortem) associada.",
            "- REQUIREMENT_WITHOUT_STORY: Requirement que não está vinculado a nenhuma Story.",
            "- STORY_WITHOUT_REQUIREMENT: Story que ainda não foi detalhada em nenhum Requirement.",
            "Analise essas inconsistências e responda estritamente em JSON com:",
            "- ai_analysis (texto): um resumo interpretando os riscos de rastreabilidade e conhecimento perdido, destacando padrões entre as lacunas.",
            "- recommendations (lista de strings): ações práticas e priorizadas para fechar primeiro as lacunas mais críticas.",
        ]
        return "\n".join(prompt_parts)

    def get_ai_response(self, prompt, gaps) -> KnowledgeGapsResponse:
        """Get the AI response for the knowledge gap analysis."""
        try:
            ai_response = self._call_llm(prompt)
            return KnowledgeGapsResponse(
                gaps=gaps,
                ai_analysis=ai_response.get("ai_analysis", ""),
                recommendations=ai_response.get("recommendations", []),
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to decode AI response: {e}")

    def get_knowledge_gaps(self) -> KnowledgeGapsResponse:
        """Retrieve the knowledge gap analysis"""
        records = self._get_all_gaps_chain()

        if not records:
            return KnowledgeGapsResponse(
                gaps=[],
                ai_analysis="",
                recommendations=[],
            )

        context = self._build_health_score_context(records)
        prompt = self._build_health_score_prompt(context)
        return self.get_ai_response(prompt, records)
