"""MMK AI Engine v0.2.0."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AIRequest:
    prompt: str
    system: str | None = None


class AIEngineError(Exception):
    """Base error for the MMK AI Engine."""


class AIEngine:
    """Provider-neutral MMK AI interface."""

    SUPPORTED_PROVIDERS = ("gemini", "openai", "local")

    def __init__(self, provider: str):
        provider = provider.lower().strip()

        if provider not in self.SUPPORTED_PROVIDERS:
            raise AIEngineError(
                f"Unsupported provider: {provider}. "
                f"Choose from: {', '.join(self.SUPPORTED_PROVIDERS)}"
            )

        self.provider = provider

    def status(self) -> dict[str, str]:
        """Return engine status without contacting an API."""
        return {
            "engine": "MMK AI Engine",
            "version": "0.2.0",
            "provider": self.provider,
            "api_request": "not made",
        }

    def create_request(
        self,
        prompt: str,
        system: str | None = None,
    ) -> AIRequest:
        """Validate and create a standard AI request."""
        if not prompt.strip():
            raise AIEngineError("Prompt cannot be empty.")

        return AIRequest(
            prompt=prompt,
            system=system,
        )
