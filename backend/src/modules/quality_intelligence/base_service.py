import logging


class QualityIntelligenceBaseService:
    def __init__(self, db_session, ai_provider):
        self.db_session = db_session
        self.ai_provider = ai_provider

    def _get_label(node):
        label = (
            sorted(node.labels)[0]
            if hasattr(node, "labels") and node.labels
            else "Artifact"
        )

        return label

    def _build_context(self, nodes):
        """
        Build a context string from a list of nodes.
        Each node is expected to have a 'title' and 'description' attribute.
        """
        context_parts = []
        for node in nodes:
            # Extract the label (type) of the node. Assumes the Neo4j driver pattern.
            label = self._get_label(node)

            # Search for properties with fallback to avoid attribute errors
            title = node.get("title", "No title")
            description = node.get("description", "No description")

            part = f"[{label}] Title: {title}\nDescription: {description}"
            context_parts.append(part)

        return "\n---\n".join(context_parts)

    def _build_prompt(self, context, health_score_data):
        """
        Build a prompt string from health score data.
        """
        main_node = (health_score_data.get("main_node", {}),)
        prompt_parts = [
            f"context: {context}",
            f"Main Node: {main_node.get('title')} (Type: {main_node.get('label')})",
            f"Nodes by Type: {health_score_data.get('nodes_by_type', {})}",
            "Answer strictly in JSON with the fields: evidence (list of objects with artifact/type/justification), ai_analysis (text), recommendations (list of strings) and risk_classification (one of LOW, MEDIUM, HIGH)"
        ]

        return "\n".join(prompt_parts)

    def _call_llm(self, prompt: str):
        """
        Call the LLM (Language Model) with the given prompt.
        """
        system_instruction = (
            "You are a QA specialist at DefectMind. "
            "Analyze the provided data and respond STRICTLY based on it. "
            "Do not use external knowledge. If the data is insufficient, declare it."
        )

        try:
            prompt = f"{system_instruction}\n\nData for analysis:\n{prompt}"
            response_llm = self.ai_provider.generate_response(prompt, temperature=0.1)
            return response_llm
        except Exception as e:
            logging.error(f"Error occurred while calling LLM: {e}")
            raise
