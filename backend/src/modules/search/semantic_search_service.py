from backend.src.core.embeddings.embedding_service import EmbeddingService
from backend.src.modules.search.schema import SearchResult

index_label = {"Story":"story_embedding_index", "Requirement":"requirement_embedding_index", "TestCase":"testcase_embedding_index", "BugReport":"bugreport_embedding_index", "Incident":"incident_embedding_index", "PostMortem":"postmortem_embedding_index"}

class SemanticSearchService:
    def __init__(
        self, neo4j_session, embedding_service: EmbeddingService
    ):
        self.db = neo4j_session
        self.embedding = embedding_service

    def search_results (self, result: str, limit: int):
        search_result = []
        for record in result[:limit]:
            node = record["node"]
            props = {k: v for k, v in dict(node).items() if k != "embedding"}
            search_result.append(SearchResult(
                id=node["id"],
                label=record["label"],
                properties=props,
                score=record["score"]
            ))
        return search_result


    def _search(self, request_text: str, filter: str, limit: int):
        result = []
        vector = self.embedding.encode(request_text)
        query = """
            CALL db.index.vector.queryNodes($index_name, $limit, $vector)
            YIELD node, score
            RETURN node, score, labels(node)[0] AS label
            """
        if filter in index_label:
            index_name = index_label[filter]
            result.extend(self.db.run(query, index_name=index_name, limit=limit, vector=vector))
        else:
            for filter in index_label.values():
                result.extend(self.db.run(query, index_name=index_name, limit=limit, vector=vector))
            
        result = sorted(result, key=lambda r: r["score"], reverse=True)
        return self.search_results(result, limit)