class QualityIntelligenceBaseService:
    def __init__(self, db_session, ai_provider):
        self.db_session = db_session
        self.ai_provider = ai_provider

    def _build_context(self, nodes):
        """
        Build a context string from a list of nodes.
        Each node is expected to have a 'title' and 'description' attribute.
        """
        context_parts = []
        for node in nodes:
            # Extract the label (type) of the node. Assumes the Neo4j driver pattern.
            label = (
                sorted(node.labels)[0]
                if hasattr(node, "labels") and node.labels
                else "Artifact"
            )

            # Search for properties with fallback to avoid attribute errors
            title = node.get("title", "No title")
            description = node.get("description", "No description")

            part = f"[{label}] Title: {title}\nDescription: {description}"
            context_parts.append(part)

        return "\n---\n".join(context_parts)

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
            print(f"Error occurred while calling LLM: {e}")
            raise
