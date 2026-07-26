import json
import os

os.environ.setdefault("GEMINI_API_KEY", "fake-key-for-tests")


from unittest.mock import MagicMock

import pytest

from backend.src.core.ai.gemini_provider import GeminiProvider


def test_generate_json_returns_dict(provider):
    """Ensures that generate_json returns a valid dict from the model's response."""
    fake_response_text = json.dumps({"stories": [], "requirements": []})

    provider.client.models.generate_content.return_value = MagicMock(
        text=fake_response_text
    )

    result = provider.generate_json(prompt="Generate a banking scenario.")

    assert isinstance(result, dict)
    assert "stories" in result
    assert "requirements" in result


def test_generate_json_raises_on_invalid_json(provider):
    """Ensures that generate_json raises an error if the model returns invalid JSON."""
    provider.client.models.generate_content.return_value = MagicMock(
        text="This is not a json"
    )

    with pytest.raises(json.JSONDecodeError):
        provider.generate_json(prompt="Generate a banking scenario.")


def test_init_raises_without_api_key():
    """Ensures that GeminiProvider raises a ValueError if the key is not provided."""
    with pytest.raises(ValueError, match="Gemini API key"):
        GeminiProvider(api_key=None)
