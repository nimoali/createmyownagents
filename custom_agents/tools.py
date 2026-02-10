"""Built-in tools that custom agents can use."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import ast
from typing import Callable


class ToolError(RuntimeError):
    """Raised when tool execution fails."""


@dataclass(frozen=True, slots=True)
class ToolSpec:
    name: str
    description: str
    handler: Callable[[str], str]


def _time_tool(_: str) -> str:
    """Return current UTC timestamp."""
    return datetime.now(tz=timezone.utc).isoformat()


def _echo_tool(argument: str) -> str:
    """Return input as output."""
    return argument


def _safe_calculator(expression: str) -> str:
    """Evaluate a math expression with a strict AST allow-list."""
    if not expression.strip():
        raise ToolError("calculator tool requires an expression")

    allowed_node_types = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Constant,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Mod,
        ast.Pow,
        ast.FloorDiv,
        ast.UAdd,
        ast.USub,
        ast.Load,
    )

    try:
        parsed = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise ToolError(f"Invalid expression: {expression!r}") from exc

    for node in ast.walk(parsed):
        if not isinstance(node, allowed_node_types):
            raise ToolError("Expression contains unsupported operations")

    try:
        result = eval(compile(parsed, filename="<calculator>", mode="eval"), {"__builtins__": {}})
    except ZeroDivisionError as exc:
        raise ToolError("Division by zero") from exc
    except Exception as exc:  # pragma: no cover - defensive path
        raise ToolError("Unable to evaluate expression") from exc

    return str(result)


BUILTIN_TOOLS: dict[str, ToolSpec] = {
    "time": ToolSpec(
        name="time",
        description="Returns the current UTC time in ISO-8601 format.",
        handler=_time_tool,
    ),
    "echo": ToolSpec(
        name="echo",
        description="Returns exactly the input string.",
        handler=_echo_tool,
    ),
    "calculator": ToolSpec(
        name="calculator",
        description="Evaluates basic arithmetic expressions like '(2 + 3) * 4'.",
        handler=_safe_calculator,
    ),
}


def list_tool_names() -> list[str]:
    return sorted(BUILTIN_TOOLS)


def describe_tools(tool_names: list[str]) -> str:
    """Render a small help string for enabled tools."""
    if not tool_names:
        return "No tools enabled."

    lines = []
    for name in tool_names:
        spec = BUILTIN_TOOLS.get(name)
        if spec is None:
            lines.append(f"- {name}: unknown tool")
        else:
            lines.append(f"- {spec.name}: {spec.description}")
    return "\n".join(lines)


def run_builtin_tool(tool_name: str, argument: str) -> str:
    """Run one built-in tool by name."""
    spec = BUILTIN_TOOLS.get(tool_name)
    if spec is None:
        allowed = ", ".join(list_tool_names())
        raise ToolError(f"Unknown tool '{tool_name}'. Available: {allowed}")
    return spec.handler(argument)
