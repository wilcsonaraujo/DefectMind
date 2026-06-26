import json
from google.genai import types
from typing import Any, Dict

from google import genai
from backend.src.core.ai.provider import AIProvider
from backend.src.core.config import settings


class GeminiProvider(AIProvider):
    def __init__(self, api_key: str = settings.GEMINI_API_KEY):
        if not api_key:
            raise ValueError("The Gemini API key was not found.")

        self.client = genai.Client(api_key)
        self.gemini_model = "gemini-1.5-flash"

    def _call_model(self, prompt: str, config=None) -> str:
        response = self.client.models.generate_content(
            model=self.gemini_model, contents=prompt, config=config
        )
        return response.text

    def generate_json(self, prompt: str, schema: Any = None) -> Dict[str, Any]:

        config_args = {"response_mime_type": "application/json"}

        if schema:
            config_args["response_schema"] = schema

        config = types.GenerateContentConfig(**config_args)

        response = self._call_model(prompt=prompt, config=config)
        response = response.strip()

        return json.loads(response)
