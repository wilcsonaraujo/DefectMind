from backend.src.core.ai.deepseek_provider import DeepSeekProvider
from backend.src.core.ai.gemini_provider import GeminiProvider
from backend.src.core.ai.groq_provider import GroqProvider
from backend.src.core.ai.provider import AIProvider
from backend.src.core.config import settings


def get_ai_provider() -> AIProvider:
    ai_provider = settings.AI_PROVIDER.lower().strip()

    if ai_provider == "deepseek":
        return DeepSeekProvider(api_key=settings.DEEPSEEK_API_KEY)
    elif ai_provider == "gemini":
        return GeminiProvider(api_key=settings.GEMINI_API_KEY)
    elif ai_provider == "groq":
        return GroqProvider(api_key=settings.GROQ_API_KEY)
    else:
        raise ValueError(
            f"AI provider '{ai_provider}' is not supported. Valid values: 'deepseek', 'gemini', 'groq'."
        )
