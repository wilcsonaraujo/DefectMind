from neo4j import GraphDatabase
from core.config import settings

URL = settings.NEO4J_URI
AUTH = settings.NEO4J_USER, settings.NEO4J_PASSWORD


# Driver criation and executing a test consulting the database
def get_neo4j_driver():
    try:
        driver = GraphDatabase.driver(URL, auth=AUTH)
        driver.verify_connectivity()  # Test the connection
        return driver
    except Exception as e:
        print(f"Error connecting to Neo4j driver: {e}")
        raise


def get_neo4j_session():
    driver = get_neo4j_driver()
    session = driver.session()
    try:
        yield session
    finally:
        session.close()
