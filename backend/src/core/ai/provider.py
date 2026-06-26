from abc import ABC, abstractmethod
from typing import Any, Dict


class AIProvider(ABC):

    @abstractmethod
    def generate_json(self, prompt: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def _call_model(self, prompt: str) -> str:
        pass
