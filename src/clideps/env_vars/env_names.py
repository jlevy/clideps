from __future__ import annotations

from enum import StrEnum
from logging import getLogger

log = getLogger(__name__)


class EnvName(StrEnum):
    """
    Convenience names for some common API environment variables.
    Any other env key is allowed too. This could be expanded.
    """

    OPENAI_API_KEY = "OPENAI_API_KEY"
    ANTHROPIC_API_KEY = "ANTHROPIC_API_KEY"
    GEMINI_API_KEY = "GEMINI_API_KEY"
    AZURE_API_KEY = "AZURE_API_KEY"
    XAI_API_KEY = "XAI_API_KEY"
    DEEPSEEK_API_KEY = "DEEPSEEK_API_KEY"
    MISTRAL_API_KEY = "MISTRAL_API_KEY"
    PERPLEXITYAI_API_KEY = "PERPLEXITYAI_API_KEY"
    DEEPGRAM_API_KEY = "DEEPGRAM_API_KEY"
    GROQ_API_KEY = "GROQ_API_KEY"
    FIRECRAWL_API_KEY = "FIRECRAWL_API_KEY"
    EXA_API_KEY = "EXA_API_KEY"

    @classmethod
    def api_env_name(cls, provider_name: str) -> EnvName | None:
        """
        Get the ApiKey for a name, i.e. "openai" -> "OPENAI_API_KEY". Works for
        the keys in this common list.
        """
        return getattr(cls, provider_name.upper() + "_API_KEY", None)

    @property
    def api_provider(self) -> str | None:
        """
        Get the lowercase provider name for an API ("openai", "azure", etc.),
        if it's an API key.
        This matches LiteLLM's provider names.
        """
        if self.value.endswith("_API_KEY"):
            return self.value.removesuffix("_API_KEY").lower()
        return None

    def display_str(self, show_provider: bool = True) -> str:
        api_provider = self.api_provider
        if api_provider and show_provider:
            return f"{api_provider} ({self.value})"
        else:
            return self.value


def get_all_common_env_names() -> list[str]:
    """
    Get a list of all some common environment variables we know about.
    """
    return [var.value for var in EnvName]
