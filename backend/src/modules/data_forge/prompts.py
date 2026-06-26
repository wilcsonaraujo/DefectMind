import json

_output_example = {
    "meta": {"nome": "DefectMind", "version": "2.0", "language": "English"},
    "role": "You are a Product Owner and Quality Assurance specialist in the banking sector. Your role involves creating user stories, system requirements, test cases, bug reports, and incident reports, as well as conducting post-mortems.",
    "context": "You are helping the user populate a Neo4j database with artifacts (Stories, Requirements, Test Cases, Bug Reports, Incidents e Postmortems). These artifacts will have relationships (Stories -> Requirements -> Test Cases -> Bug Reports -> Incidents -> Postmortems). The user wants the response in JSON format, containing all populated elements and presented in an easy-to-understand way.",
    "task": "Generate exactly {batch_size} stories and their related artifacts for a banking system.",
    "constraints": [
        "Use temp_id (integer, starting at 1) in every entity",
        "Use reference fields (story_temp_id, requirement_temp_id, testcase_temp_id, bug_temp_id, incident_temp_id) to map relationships",
        "priority must be one of: Low, Medium, High",
        "severity must be one of: Low, Medium, High, Critical",
        "impact must be one of: Low, Medium, High, Critical",
        "All text must be in English",
        "Generate coherent and realistic banking scenarios",
    ],
    "output_expected": {
        "stories": [{"temp_id": 1, "title": "...", "description": "..."}],
        "requirements": [
            {
                "temp_id": 2,
                "story_temp_id": 1,
                "description": "...",
                "priority": "High",
            }
        ],
        "testcases": [
            {
                "temp_id": 3,
                "requirement_temp_id": 2,
                "title": "...",
                "steps": "...",
                "expected_result": "...",
            }
        ],
        "bug_reports": [
            {
                "temp_id": 4,
                "testcase_temp_id": 3,
                "title": "...",
                "description": "...",
                "severity": "Medium",
            }
        ],
        "incidents": [
            {
                "temp_id": 5,
                "bug_temp_id": 4,
                "title": "...",
                "description": "...",
                "impact": "Critical",
            }
        ],
        "postmortems": [
            {
                "temp_id": 6,
                "incident_temp_id": 5,
                "root_cause": "...",
                "resolution": "...",
                "lessons_learned": "...",
            }
        ],
    },
}


def build_banking_prompt(batch_size: int) -> str:

    _output_example["task"] = _output_example["task"].format(batch_size=batch_size)
    prompt = json.dumps(_output_example, indent=2)
    return prompt
