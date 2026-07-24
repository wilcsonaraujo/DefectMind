from neo4j import GraphDatabase

from backend.src.core.config import settings

_driver = None

# Driver criation and executing a test consulting the database
def init_neo4j_driver():
    if not settings.NEO4J_URI:
        return  # Neo4j not configured, skip driver initialization
    global _driver
    _driver = GraphDatabase.driver(
        settings.NEO4J_URI,
        auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
    )

def close_neo4j_driver():
    global _driver
    if _driver:
        _driver.close()
        _driver = None


def get_neo4j_session():
    if _driver is None:
        yield None
        return
    session = _driver.session()
    try:
        yield session
    finally:
        session.close()
