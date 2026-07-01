from backend.src.modules.search.schemas import NodeByType


class GraphService:

    def __init__(self, neo4j_session):
        self.db = neo4j_session

    def _get_total_nodes(self):
        query = "MATCH (n) RETURN count(n) AS total_nodes"
        result = self.db.run(query)
        return result.single()["total_nodes"]

    def _get_total_edges(self):
        query = "MATCH ()-[r]->() RETURN count(r) AS total_edges"
        result = self.db.run(query)
        return result.single()["total_edges"]

    def _get_nodes_by_type(self):
        query = """
        MATCH (n) RETURN labels(n)[0] AS label, count(n) AS total ORDER BY total DESC
        """
        result = self.db.run(query)
        nodes_by_type = NodeByType()
        for record in result:
            label = record["label"]
            count = record["total"]
            if hasattr(nodes_by_type, label):
                setattr(nodes_by_type, label, count)
        return nodes_by_type

    def _get_most_connected_nodes(self, limit = 10):
        query = """
        MATCH (n)-[r]->()
        RETURN n.id AS id, labels(n)[0] AS label, n.title AS title, count(r) AS degree
        ORDER BY degree DESC
        LIMIT $limit
        """
        result = self.db.run(query, limit=limit)
        most_connected_nodes = []
        for record in result:
            most_connected_nodes.append(
                {
                    "id": record["id"],
                    "label": record["label"],
                    "title": record["title"],
                    "degree": record["degree"],
                }
            )
        return most_connected_nodes

    def _get_isolated_nodes(self):
        query = """
        MATCH (n)
        WHERE NOT (n)-[]->() AND NOT ()-[]->(n)
        RETURN n.id AS id, labels(n)[0] AS label, n.title AS title
        """
        result = self.db.run(query)
        isolated_nodes = []
        for record in result:
            isolated_nodes.append(
                {
                    "id": record["id"],
                    "label": record["label"],
                    "title": record["title"],
                }
            )
        return isolated_nodes

    def _get_avg_degree(self):
        total_nodes = self._get_total_nodes()
        total_edges = self._get_total_edges()
        if total_nodes == 0:
            return 0
        return total_edges / total_nodes

    def _get_density(self):
        total_nodes = self._get_total_nodes()
        total_edges = self._get_total_edges()
        if total_nodes <= 1:
            return 0
        return total_edges / (total_nodes * (total_nodes - 1))

    def _get_graph_stats(self):
        total_nodes = self._get_total_nodes()
        total_edges = self._get_total_edges()
        nodes_by_type = self._get_nodes_by_type()
        most_connected_nodes = self._get_most_connected_nodes()
        isolated_nodes = self._get_isolated_nodes()
        avg_degree = self._get_avg_degree()
        density = self._get_density()

        return {
            "total_nodes": total_nodes,
            "total_edges": total_edges,
            "nodes_by_type": nodes_by_type,
            "most_connected_nodes": most_connected_nodes,
            "isolated_nodes": isolated_nodes,
            "avg_degree": avg_degree,
            "density": density,
        }
