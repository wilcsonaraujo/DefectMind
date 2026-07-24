import logging

logger = logging.getLogger(__name__)

def create_vector_indexes(session):

    entities = [
        {"label": "Story",     "index_name": "story_embedding_index"},
        {"label": "Requirement", "index_name": "requirement_embedding_index"},
        {"label": "TestCase",  "index_name": "testcase_embedding_index"},
        {"label": "BugReport", "index_name": "bugreport_embedding_index"},
        {"label": "Incident",  "index_name": "incident_embedding_index"},
        {"label": "PostMortem","index_name": "postmortem_embedding_index"},
    ]

    for entity in entities:
        index_query = f"""
            CREATE VECTOR INDEX {entity['index_name']} IF NOT EXISTS
            FOR (n:{entity['label']}) ON (n.embedding)
            OPTIONS {{indexConfig: {{`vector.dimensions`: 384, `vector.similarity_function`: 'cosine'}}}}
        """
        try:
            session.run(index_query)
            logger.info(f"Index {entity['index_name']} created")
        except Exception as e:
            logger.error(f"Error creating index {entity['index_name']}: {e}")
