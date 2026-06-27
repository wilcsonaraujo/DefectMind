import json
from typing import Any, Dict

from openai import OpenAI

from backend.src.core.ai.provider import AIProvider
from backend.src.core.config import settings


class DeepSeekProvider(AIProvider):
    def __init__(self, api_key: str = settings.DEEPSEEK_API_KEY):
        if not api_key:
            raise ValueError("The DeepSeek API key was not found.")

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com",
        )
        self.model = "deepseek-chat"

    def _call_model(self, prompt: str, config: dict = None) -> str:
        messages = [{"role": "user", "content": prompt}]

        kwargs = {
            "model": self.model,
            "messages": messages,
        }

        if config:
            kwargs.update(config)

        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content

    def generate_json(self, prompt: str, schema: Any = None) -> Dict[str, Any]:
        config = {
            "response_format": {"type": "json_object"},
        }

        response = self._call_model(prompt=prompt, config=config)
        response = response.strip()

        return json.loads(response)