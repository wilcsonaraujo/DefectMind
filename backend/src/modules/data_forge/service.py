from datetime import datetime, timezone
import logging
import uuid

from pydantic import ValidationError
from backend.src.core.ai.provider import AIProvider
from backend.src.modules.data_forge.prompts import build_prompt
from backend.src.modules.data_forge.schemas import DataForgeOutput


class DataForgeService:

    def __init__(self, ai_provider: AIProvider, neo4j_session):
        self.ai = ai_provider
        self.db = neo4j_session

    def _insert_batch(self, batch: DataForgeOutput):
        created_at = datetime.now(timezone.utc).isoformat()

        story_id_map = {s.temp_id: str(uuid.uuid4()) for s in batch.stories}
        requirement_id_map = {r.temp_id: str(uuid.uuid4()) for r in batch.requirements}
        testcase_id_map = {t.temp_id: str(uuid.uuid4()) for t in batch.testcases}
        bugreport_id_map = {b.temp_id: str(uuid.uuid4()) for b in batch.bug_reports}
        incident_id_map = {i.temp_id: str(uuid.uuid4()) for i in batch.incidents}
        postmortems_id_map = {p.temp_id: str(uuid.uuid4()) for p in batch.postmortems}

        stories_query = """MERGE (s:Story {id: $id})
        SET s.title = $title, s.description = $description, s.created_at = $created_at
        """
        requirements_query = """MERGE (r:Requirement {id: $id})
        SET r.description = $description, r.priority = $priority, r.created_at = $created_at
        """
        testcases_query = """MERGE (t:TestCase {id: $id})
        SET t.title = $title, t.steps = $steps, t.expected_result = $expected_result, t.created_at = $created_at
        """
        bug_reports_query = """MERGE (b:BugReport {id: $id})
        SET b.title = $title, b.description = $description, b.severity = $severity, b.created_at = $created_at
        """
        incidents_query = """MERGE (i:Incident {id: $id})
        SET i.title = $title, i.description = $description, i.impact = $impact, i.created_at = $created_at
        """
        postmortems_query = """MERGE (p:PostMortem {id: $id})
        SET p.root_cause = $root_cause, p.resolution = $resolution, p.lessons_learned = $lessons_learned, p.created_at = $created_at
        """
        for story in batch.stories:
            uuid_real = story_id_map[story.temp_id]
            self.db.run(
                stories_query,
                id=uuid_real,
                title=story.title,
                description=story.description,
                created_at=created_at,
            )
        for requirement in batch.requirements:
            uuid_real = requirement_id_map[requirement.temp_id]
            self.db.run(
                requirements_query,
                id=uuid_real,
                description=requirement.description,
                priority=requirement.priority.value,
                created_at=created_at,
            )
        for testcase in batch.testcases:
            uuid_real = testcase_id_map[testcase.temp_id]
            self.db.run(
                testcases_query,
                id=uuid_real,
                title=testcase.title,
                steps=testcase.steps,
                expected_result=testcase.expected_result,
                created_at=created_at,
            )
        for bug_report in batch.bug_reports:
            uuid_real = bugreport_id_map[bug_report.temp_id]
            self.db.run(
                bug_reports_query,
                id=uuid_real,
                title=bug_report.title,
                description=bug_report.description,
                severity=bug_report.severity.value,
                created_at=created_at,
            )
        for incident in batch.incidents:
            uuid_real = incident_id_map[incident.temp_id]
            self.db.run(
                incidents_query,
                id=uuid_real,
                title=incident.title,
                description=incident.description,
                impact=incident.impact.value,
                created_at=created_at,
            )
        for postmortem in batch.postmortems:
            uuid_real = postmortems_id_map[postmortem.temp_id]
            self.db.run(
                postmortems_query,
                id=uuid_real,
                root_cause=postmortem.root_cause,
                resolution=postmortem.resolution,
                lessons_learned=postmortem.lessons_learned,
                created_at=created_at,
            )

        for requirement in batch.requirements:
            uuid_mother = story_id_map[requirement.story_temp_id]
            uuid_daughter = requirement_id_map[requirement.temp_id]
            relation_query = """
            MATCH (s:Story {id: $story_id}), (r:Requirement {id: $req_id})
            MERGE (s)-[:HAS_REQUIREMENT]->(r)
            """
            self.db.run(relation_query, story_id=uuid_mother, req_id=uuid_daughter)

        for testcase in batch.testcases:
            uuid_mother = requirement_id_map[testcase.requirement_temp_id]
            uuid_daughter = testcase_id_map[testcase.temp_id]
            relation_query = """
            MATCH (r:Requirement {id: $req_id}), (t:TestCase {id: $tc_id})
            MERGE (r)-[:COVERED_BY]->(t)
            """
            self.db.run(relation_query, req_id=uuid_mother, tc_id=uuid_daughter)

        for bugs in batch.bug_reports:
            uuid_mother = testcase_id_map[bugs.testcase_temp_id]
            uuid_daughter = bugreport_id_map[bugs.temp_id]
            relation_query = """
            MATCH (t:TestCase {id: $tc_id}), (b:BugReport {id: $bug_id})
            MERGE (t)-[:FOUND]->(b)
            """
            self.db.run(relation_query, tc_id=uuid_mother, bug_id=uuid_daughter)

        for incident in batch.incidents:
            uuid_mother = bugreport_id_map[incident.bug_temp_id]
            uuid_daughter = incident_id_map[incident.temp_id]
            relation_query = """
            MATCH (b:BugReport {id: $bug_id}), (i:Incident {id: $incident_id})
            MERGE (b)-[:CAUSED]->(i)
            """
            self.db.run(relation_query, bug_id=uuid_mother, incident_id=uuid_daughter)

        for postmortem in batch.postmortems:
            uuid_mother = incident_id_map[postmortem.incident_temp_id]
            uuid_daughter = postmortems_id_map[postmortem.temp_id]
            relation_query = """
            MATCH (i:Incident {id: $incident_id}), (p:PostMortem {id: $pm_id})
            MERGE (i)-[:ROOT_CAUSE]->(p)
            """
            self.db.run(relation_query, incident_id=uuid_mother, pm_id=uuid_daughter)

    def generate(self, num_stories: int, batch_size: int) -> dict:
        num_batches = num_stories // batch_size

        totals = {
            "stories": 0,
            "requirements": 0,
            "test_cases": 0,
            "bug_reports": 0,
            "incidents": 0,
            "post_mortems": 0,
            "batches_processed": 0,
            "batches_failed": 0,
        }

        for iteration in range(num_batches):
            prompt = build_prompt(batch_size)
            response_llm = self.ai.generate_json(prompt)

            try:
                batch = DataForgeOutput.model_validate(response_llm)
            except ValidationError as e:
                logging.warning(f"Batch {iteration} failed validation: {e}")
                totals["batches_failed"] += 1
                continue

            self._insert_batch(batch)
            totals["stories"] += len(batch.stories)
            totals["requirements"] += len(batch.requirements)
            totals["test_cases"] += len(batch.testcases)
            totals["bug_reports"] += len(batch.bug_reports)
            totals["incidents"] += len(batch.incidents)
            totals["post_mortems"] += len(batch.postmortems)
            totals["batches_processed"] += 1

        return totals
