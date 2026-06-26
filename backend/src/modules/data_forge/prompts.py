from typing import List

story_json = {"temp_id": int, "title": str, "description": str}

requirement_json = {
    "temp_id": int,
    "story_temp_id": int,
    "description": str,
    "priority": ["Low", "Medium", "High"],
}

testcase_json = {
    "temp_id": int,
    "requirement_temp_id": int,
    "title": str,
    "steps": str,
    "expected_result": str,
}

bugreport_json = {
    "temp_id": int,
    "testcase_temp_id": int,
    "title": str,
    "description": str,
    "severity": ["Low", "Medium", "High", "Critical"],
}

incident_json = {
    "temp_id": int,
    "bug_temp_id": int,
    "title": str,
    "description": str,
    "impact": ["Low", "Medium", "High", "Critical"],
}

postmortem_json = {
    "temp_id": int,
    "incident_temp_id": int,
    "root_cause": str,
    "resolution": str,
    "lessons_learned": str,
}

dataforgeoutput_json = {
    "stories": List[story_json],
    "requirements": List[requirement_json],
    "testcases": List[testcase_json],
    "bugsreport": List[bugreport_json],
    "incidents": List[incident_json],
    "postmortems": List[postmortem_json],
}

llm_prompt_json = {
    "meta": {"nome": "DefectMind", "version": "2.0", "language": "English"},
    "role": "You are a Product Owner and Quality Assurance specialist in the banking sector. Your role involves creating user stories, system requirements, test cases, bug reports, and incident reports, as well as conducting post-mortems.",
    "context": "You are helping the user populate a Neo4j database with artifacts (Stories, Requirements, Test Cases, Bug Reports, Incidents e Postmortems). These artifacts will have relationships (Stories -> Requirements -> Test Cases -> Bug Reports -> Incidents -> Postmortems). The user wants the response in JSON format, containing all populated elements and presented in an easy-to-understand way.",
    "task": "Create well-structured artifacts (Stories, Requirements, Test Cases, Bug Reports, Incidents e Postmortems) that strictly follow the fields shown in the output section. The artifacts must relate to banking processes and systems. The attributes will have relationships; therefore, include temporary IDs, just as shown in the expected output.",
    "constraints": [
        "The artifacts must be written in English.",
        "All fields must be filled out in a coherent and connected manner.",
        "The 'Output_expected' field describes the expected format of the AI's response.",
        "Avoid ambiguity and be specific in the instructions.",
        "The final artifacts must be suitable for insertion into Neo4j.",
    ],
    "output_expected": {
        "stories": List[story_json],
        "requirements": List[requirement_json],
        "testcases": List[testcase_json],
        "bugsreport": List[bugreport_json],
        "incidents": List[incident_json],
        "postmortems": List[postmortem_json],
    },
}
