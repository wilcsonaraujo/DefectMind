def get_node_label(node, fallback: str = "Unknown") -> str:
    """
    Return a Neo4j node's label deterministically.
    """
    if hasattr(node, "labels") and node.labels:
        return min(node.labels)
    return fallback
