from abc import ABC, abstractmethod
from typing import Any, dict


class AIProvider(ABC):

    @abstractmethod
    def generate_json(self, prompt: str) -> dict[str, Any]:
        pass

    @abstractmethod
    def _call_model(self, prompt: str) -> str:
        pass
