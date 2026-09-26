"""Gemini provider for MMK AI Engine v0.1.0."""

import os

from google import genai


class GeminiProviderError(Exception):
    """Base error for the MMK Gemini provider."""


class GeminiProvider:
    """Gemini implementation for the MMK AI Engine."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise GeminiProviderError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(api_key=self.api_key)

    def generate(
        self,
        prompt: str,
        system: str | None = None,
        model: str = "gemini-3.8-flash",
    ) -> str:
        """Generate a response using Gemini."""
        if not prompt.strip():
            raise GeminiProviderError("Prompt cannot be empty.")

        config = None

        if system:
            config = {
                "system_instruction": system,
            }

        response = self.client.models.generate_content(
            model=model,
            contents=prompt,
            config=config,
        )

        return response.text or ""
