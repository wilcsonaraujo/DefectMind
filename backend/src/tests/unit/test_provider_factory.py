import os
import pytest
from unittest.mock import patch

os.environ.setdefault("DEEPSEEK_API_KEY", "fake-deepseek-key")
os.environ.setdefault("GEMINI_API_KEY", "fake-gemini-key")

from backend.src.core.ai.provider_factory import get_ai_provider
from backend.src.core.ai.deepseek_provider import DeepSeekProvider
from backend.src.core.ai.gemini_provider import GeminiProvider


def test_get_ai_provider_returns_deepseek():
    """Quando AI_PROVIDER=deepseek, return DeepSeekProvider."""
    with patch("backend.src.core.ai.provider_factory.settings") as mock_settings:
        mock_settings.AI_PROVIDER = "deepseek"
        mock_settings.DEEPSEEK_API_KEY = "fake-deepseek-key"
        with patch("backend.src.core.ai.deepseek_provider.OpenAI"):
            provider = get_ai_provider()
    assert isinstance(provider, DeepSeekProvider)


def test_get_ai_provider_returns_gemini():
    """Quando AI_PROVIDER=gemini, return GeminiProvider."""
    with patch("backend.src.core.ai.provider_factory.settings") as mock_settings:
        mock_settings.AI_PROVIDER = "gemini"
        mock_settings.GEMINI_API_KEY = "fake-gemini-key"
        with patch("backend.src.core.ai.gemini_provider.genai"):
            provider = get_ai_provider()
    assert isinstance(provider, GeminiProvider)


def test_get_ai_provider_case_insensitive():
    """The factory accepts values ​​in uppercase or with spaces."""
    with patch("backend.src.core.ai.provider_factory.settings") as mock_settings:
        mock_settings.AI_PROVIDER = "  DeepSeek  "
        mock_settings.DEEPSEEK_API_KEY = "fake-deepseek-key"
        with patch("backend.src.core.ai.deepseek_provider.OpenAI"):
            provider = get_ai_provider()
    assert isinstance(provider, DeepSeekProvider)


def test_get_ai_provider_raises_on_invalid_value():
    """An unsupported value raises a ValueError with the name of the received value."""
    with patch("backend.src.core.ai.provider_factory.settings") as mock_settings:
        mock_settings.AI_PROVIDER = "openai"
        with pytest.raises(ValueError, match="openai"):
            get_ai_provider()


def test_get_ai_provider_raises_when_deepseek_key_missing():
    """AI_PROVIDER=deepseek without DEEPSEEK_API_KEY give ValueError."""
    with patch("backend.src.core.ai.provider_factory.settings") as mock_settings:
        mock_settings.AI_PROVIDER = "deepseek"
        mock_settings.DEEPSEEK_API_KEY = None
        with pytest.raises(ValueError):
            get_ai_provider()
