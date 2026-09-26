"""OpenAI provider for MMK AI Engine v0.1.0."""

import os

from openai import OpenAI


class OpenAIProviderError(Exception):
    """Base error for the MMK OpenAI provider."""


class OpenAIProvider:
    """OpenAI implementation for the MMK AI Engine."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            raise OpenAIProviderError(
                "OPENAI_API_KEY is not configured."
            )

        self.client = OpenAI(api_key=self.api_key)

    def generate(
        self,
        prompt: str,
        system: str | None = None,
        model: str = "gpt-5.6",
    ) -> str:
        """Generate a response using OpenAI."""
        if not prompt.strip():
            raise OpenAIProviderError("Prompt cannot be empty.")

        messages = []

        if system:
            messages.append({
                "role": "system",
                "content": system,
            })

        messages.append({
            "role": "user",
            "content": prompt,
        })

        response = self.client.responses.create(
            model=model,
            input=messages,
        )

        return response.output_text or ""
