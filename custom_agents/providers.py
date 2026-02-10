"""LLM provider interfaces and implementations."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from typing import Protocol
from urllib import error, request

from .config import AgentConfig


@dataclass(slots=True, frozen=True)
class ChatMessage:
    role: str
    content: str


class ProviderError(RuntimeError):
    """Raised when a provider cannot produce a response."""


class ChatProvider(Protocol):
    """Protocol all providers should implement."""

    def generate(self, messages: list[ChatMessage], config: AgentConfig) -> str:
        """Return assistant output for a chat message list."""


class OpenAICompatibleProvider:
    """OpenAI-compatible chat completion provider via HTTP."""

    def generate(self, messages: list[ChatMessage], config: AgentConfig) -> str:
        api_key = os.getenv(config.api_key_env)
        if not api_key:
            raise ProviderError(
                f"Environment variable '{config.api_key_env}' is not set. "
                "Set your API key before running chat."
            )

        payload = {
            "model": config.model,
            "messages": [{"role": msg.role, "content": msg.content} for msg in messages],
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
        }

        endpoint = f"{config.api_base.rstrip('/')}/chat/completions"
        req = request.Request(
            endpoint,
            method="POST",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )

        try:
            with request.urlopen(req, timeout=90) as resp:
                raw = resp.read().decode("utf-8")
        except error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            raise ProviderError(
                f"Provider HTTP {exc.code}: {details or exc.reason}"
            ) from exc
        except error.URLError as exc:
            raise ProviderError(f"Provider request failed: {exc.reason}") from exc

        try:
            data = json.loads(raw)
            choices = data["choices"]
            return choices[0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise ProviderError("Provider returned an unexpected response shape") from exc
