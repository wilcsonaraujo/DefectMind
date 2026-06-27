import logging

from neo4j import GraphDatabase


def create_vector_indexes(session):

    entities = [
        {
            "label": "s:Story",
            "index_name": "story_embedding_index",
            "property_name": "s.embedding",
        },
        {
            "label": "r:Requirement",
            "index_name": "requirement_embedding_index",
            "property_name": "r.embedding",
        },
        {
            "label": "t:TestCase",
            "index_name": "testcase_embedding_index",
            "property_name": "t.embedding",
        },
        {
            "label": "b:BugReport",
            "index_name": "bugreport_embedding_index",
            "property_name": "b.embedding",
        },
        {
            "label": "i:Incident",
            "index_name": "incident_embedding_index",
            "property_name": "i.embedding",
        },
        {
            "label": "p:PostMortem",
            "index_name": "postmortem_embedding_index",
            "property_name": "p.embedding",
        },
    ]

    with session() as session:
        for index_name, label, property_name in entities:
            index_query = f"""
            CREATE VECTOR INDEX {index_name} IF NOT EXISTS
            FOR ({label}) ON ({property_name})
            OPTIONS {{indexConfig: {{`vector.dimensions`: 384, `vector.similarity_function`: 'cosine'}}}}
            """
            try:
                session.run(index_query)
                logging.info(f"Index {index_name} created for {label}")
            except Exception as e:
                logging.error(f"Error creating index {index_name}: {e}")
