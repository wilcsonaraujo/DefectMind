from collections import Counter

from backend.src.modules.quality_intelligence.base_service import (
    QualityIntelligenceBaseService,
)
from backend.src.modules.quality_intelligence.schemas import HealthScoreResponse


class HealthScoreService(QualityIntelligenceBaseService):

    def __init__(self, neo4j_session, ai_provider):
        super().__init__(neo4j_session, ai_provider)

    def _build_health_score_prompt(self, node_id: str):
        """
        Build the health score prompt for a node in the graph database.
        """

        query = """
        MATCH (main {id: $node_id})
        OPTIONAL MATCH (main)-[r]-(connected)
        WITH main, COLLECT(DISTINCT connected) AS connected_nodes, COLLECT(DISTINCT r) AS rels
        RETURN 
        main {
            .id,
            .title,
            label: labels(main)[0],
            degree: SIZE(connected_nodes)
        } AS main_node,
        connected_nodes AS connected,
        rels AS relationships,
        SIZE(connected_nodes) AS degree,
        SIZE(rels) AS total_edges
        """

        counts = {
            "Story": 0,
            "Requirement": 0,
            "Bug": 0,
            "TestCase": 0,
            "Incident": 0,
            "PostMortem": 0,
        }

        results = list(self.db_session.run(query, node_id=node_id))
        if not results:
            return None

        main_node = results[0]["main_node"]
        connected_nodes = results[0]["connected"]
        relationships = results[0]["relationships"]
        degree = results[0]["degree"]
        total_edges = results[0]["total_edges"]

        counts = Counter(counts)

        for node in connected_nodes:
            label = self._get_label(node)
            counts[label] += 1

        total_nodes = len(connected_nodes) + 1

        return {
            "main_node": main_node,
            "total_nodes": total_nodes,
            "total_edges": total_edges,
            "nodes_by_type": dict(counts),
            "degree": degree,
            "connected_nodes": connected_nodes,
            "connected_count": len(connected_nodes),
            "relationships_count": len(relationships),
        }

    def build_health_score_prompt(self, node_id: str):
        """
        Get the health score of a node in the graph database.
        Combines context building with health score calculation.
        """

        health_score_data = self._build_health_score_prompt(node_id)

        if not health_score_data:
            return None

        context = self._build_context(health_score_data.get("connected_nodes", {}))
    
        return self._build_prompt(context, health_score_data)

    def get_ai_response(self, prompt: str) -> HealthScoreResponse:
        """
        Get the AI response for the health score analysis.
        """
        try:
            response = self._call_llm(prompt)
            ai_response = response.parse_json()
            return HealthScoreResponse(
                evidence=ai_response.get("evidence", []),
                ai_analysis=ai_response.get("ai_analysis", ""),
                recommendations=ai_response.get("recommendations", []),
                risk_classification=ai_response.get("risk_classification", "LOW"),
            )
        except Exception as e:
            raise Exception(f"Error occurred while getting AI response: {e}")
