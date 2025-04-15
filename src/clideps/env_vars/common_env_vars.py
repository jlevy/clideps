from __future__ import annotations

from enum import StrEnum
from logging import getLogger

log = getLogger(__name__)


class CommonEnvVar(StrEnum):
    """
    Convenience names for some common API environment variables.
    Any other env key is allowed too.
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
    def api_key_for(cls, provider_name: str) -> CommonEnvVar | None:
        """
        Get the ApiKey for a name, i.e. "openai" -> "OPENAI_API_KEY". Works for
        the keys in this common list.
        """
        return getattr(cls, provider_name.upper() + "_API_KEY", None)

    @property
    def api_provider_name(self) -> str:
        """
        Get the lowercase provider name for an API ("openai", "azure", etc.).
        This matches LiteLLM's provider names.
        """
        return self.value.removesuffix("_API_KEY").lower()


COMMON_ENV_VARS = [key.value for key in CommonEnvVar]
"""
Convenience list of these common environment variables.
"""
