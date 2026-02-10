"""Configuration helpers for custom agents."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any


DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_API_BASE = "https://api.openai.com/v1"


@dataclass(slots=True)
class AgentConfig:
    """Represents one custom agent definition."""

    agent_id: str
    name: str
    system_prompt: str
    description: str = ""
    model: str = DEFAULT_MODEL
    api_base: str = DEFAULT_API_BASE
    api_key_env: str = "OPENAI_API_KEY"
    temperature: float = 0.2
    max_tokens: int = 400
    tools: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "AgentConfig":
        """Build and validate a config from a dictionary."""
        required = ("agent_id", "name", "system_prompt")
        missing = [key for key in required if not payload.get(key)]
        if missing:
            missing_str = ", ".join(missing)
            raise ValueError(f"Missing required config fields: {missing_str}")

        tools = payload.get("tools") or []
        if not isinstance(tools, list):
            raise ValueError("'tools' must be a list of tool names")

        try:
            temperature = float(payload.get("temperature", 0.2))
        except (TypeError, ValueError) as exc:
            raise ValueError("'temperature' must be a number") from exc

        try:
            max_tokens = int(payload.get("max_tokens", 400))
        except (TypeError, ValueError) as exc:
            raise ValueError("'max_tokens' must be an integer") from exc

        return cls(
            agent_id=str(payload["agent_id"]),
            name=str(payload["name"]),
            system_prompt=str(payload["system_prompt"]),
            description=str(payload.get("description", "")),
            model=str(payload.get("model", DEFAULT_MODEL)),
            api_base=str(payload.get("api_base", DEFAULT_API_BASE)),
            api_key_env=str(payload.get("api_key_env", "OPENAI_API_KEY")),
            temperature=temperature,
            max_tokens=max_tokens,
            tools=[str(tool_name) for tool_name in tools],
        )


def load_agent_config(path: str | Path) -> AgentConfig:
    """Read a JSON config file and return an AgentConfig."""
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file was not found: {config_path}")

    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {config_path}: {exc}") from exc

    return AgentConfig.from_dict(payload)


def create_agent_template(agent_id: str, name: str | None = None) -> dict[str, Any]:
    """Create a starter config payload for a new custom agent."""
    display_name = name or agent_id.replace("_", " ").title()
    return {
        "agent_id": agent_id,
        "name": display_name,
        "description": f"{display_name} custom agent",
        "system_prompt": (
            "You are a helpful assistant. Keep responses clear and actionable."
        ),
        "model": DEFAULT_MODEL,
        "api_base": DEFAULT_API_BASE,
        "api_key_env": "OPENAI_API_KEY",
        "temperature": 0.2,
        "max_tokens": 400,
        "tools": ["time", "calculator"],
    }
