from fastapi import HTTPException

from backend.src.core.neo4j_utils import get_node_label

from backend.src.modules.search.schemas import (
    ImpactAnalysisResponse,
    ImpactEdge,
    ImpactNode,
)


class ImpactAnalysisService:
    def __init__(self, neo4j_session):
        self.db = neo4j_session

    def get_impact(self, node_id: str, depth: int):
        if not isinstance(depth, int):
            raise ValueError("depth must be an integer")
        if not 1 <= depth <= 10:
            raise ValueError("depth must be between 1 and 10")

        query = f"""
                MATCH (start {{id: $node_id}})-[r*1..{depth}]-(connected)
                UNWIND r AS rel
                RETURN 
                    start,
                    connected,
                    rel,
                    startNode(rel).id AS rel_source,
                    endNode(rel).id AS rel_target,
                    type(rel) AS rel_type
                """
        records = list(self.db.run(query, node_id=node_id))

        if not records:
            raise HTTPException(status_code=404, detail="Node not found")

        nodes_map = {}
        edges = []

        for record in records:
            start = record["start"]
            connected = record["connected"]
            if start["id"] not in nodes_map:
                label = get_node_label(start, fallback="Unknown")
                props = {k: v for k, v in dict(start).items() if k != "embedding"}
                nodes_map[start["id"]] = ImpactNode(
                    id=start["id"],
                    label=label,
                    properties=props,
                )

            connected = record["connected"]
            if connected["id"] not in nodes_map:
                label = get_node_label(start, fallback="Unknown")
                props = {k: v for k, v in dict(connected).items() if k != "embedding"}
                nodes_map[connected["id"]] = ImpactNode(
                    id=connected["id"],
                    label=label,
                    properties=props
                )

            edges.append(
                ImpactEdge(
                    source=record["rel_source"],
                    target=record["rel_target"],
                    type=record["rel_type"],
                )
            )

        return ImpactAnalysisResponse(
            nodes=list(nodes_map.values()),
            edges=edges,
        )
