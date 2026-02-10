"""Agent runtime and tool-call loop."""

from __future__ import annotations

from dataclasses import dataclass, field
import re

from .config import AgentConfig
from .providers import ChatMessage, ChatProvider, OpenAICompatibleProvider
from .tools import ToolError, describe_tools, list_tool_names, run_builtin_tool


TOOL_CALL_PATTERN = re.compile(r"^TOOL_CALL\s+([a-zA-Z0-9_-]+)\s*\|\s*(.*)$", re.DOTALL)


@dataclass(slots=True)
class Agent:
    """A chat agent loaded from an AgentConfig."""

    config: AgentConfig
    provider: ChatProvider = field(default_factory=OpenAICompatibleProvider)
    max_tool_rounds: int = 2

    def __post_init__(self) -> None:
        unknown = [name for name in self.config.tools if name not in list_tool_names()]
        if unknown:
            known = ", ".join(list_tool_names())
            unknown_str = ", ".join(unknown)
            raise ValueError(f"Unknown configured tool(s): {unknown_str}. Available: {known}")

    def respond(self, user_message: str, history: list[ChatMessage] | None = None) -> str:
        """Respond to user input, handling optional tool calls."""
        prior = history[:] if history else []

        system_prompt = self._build_system_prompt()
        messages: list[ChatMessage] = [ChatMessage(role="system", content=system_prompt)]
        messages.extend(prior)
        messages.append(ChatMessage(role="user", content=user_message))

        for _ in range(self.max_tool_rounds + 1):
            assistant_text = self.provider.generate(messages, self.config)
            maybe_tool_call = self._parse_tool_call(assistant_text)
            if maybe_tool_call is None:
                return assistant_text

            tool_name, tool_input = maybe_tool_call
            if tool_name not in self.config.tools:
                return (
                    f"Tool '{tool_name}' is not enabled for this agent. "
                    f"Enabled tools: {', '.join(self.config.tools) or 'none'}."
                )

            try:
                tool_output = run_builtin_tool(tool_name, tool_input)
            except ToolError as exc:
                tool_output = f"Tool error: {exc}"

            messages.append(ChatMessage(role="assistant", content=assistant_text))
            messages.append(
                ChatMessage(
                    role="user",
                    content=(
                        f"Tool '{tool_name}' output:\n{tool_output}\n\n"
                        "Continue helping the user using this tool result."
                    ),
                )
            )

        return "I hit the maximum number of tool calls in one response. Please try again."

    @staticmethod
    def handle_tool_command(raw_command: str) -> str:
        """Handle manual /tool command from the CLI."""
        parts = raw_command.strip().split(maxsplit=2)
        if len(parts) < 2:
            raise ToolError("Usage: /tool <name> [argument]")

        tool_name = parts[1]
        argument = parts[2] if len(parts) >= 3 else ""
        return run_builtin_tool(tool_name, argument)

    def _build_system_prompt(self) -> str:
        if not self.config.tools:
            return self.config.system_prompt

        tool_help = describe_tools(self.config.tools)
        return (
            f"{self.config.system_prompt}\n\n"
            "Available tools:\n"
            f"{tool_help}\n\n"
            "If you need a tool, respond exactly with this format and nothing else:\n"
            "TOOL_CALL <tool_name> | <tool_input>\n"
            "After tool output is provided, continue with the final answer."
        )

    @staticmethod
    def _parse_tool_call(text: str) -> tuple[str, str] | None:
        match = TOOL_CALL_PATTERN.match(text.strip())
        if not match:
            return None
        return match.group(1), match.group(2)
