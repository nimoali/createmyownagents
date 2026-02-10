"""Command line interface for creating and chatting with custom agents."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .agent import Agent
from .config import create_agent_template, load_agent_config
from .providers import ChatMessage, ProviderError
from .tools import ToolError, describe_tools, list_tool_names


def _cmd_create(args: argparse.Namespace) -> int:
    payload = create_agent_template(args.agent_id, name=args.name)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Created agent template at: {out_path}")
    return 0


def _cmd_chat(args: argparse.Namespace) -> int:
    config = load_agent_config(args.config)
    agent = Agent(config=config)
    history: list[ChatMessage] = []

    if args.message:
        try:
            answer = agent.respond(args.message, history=history)
        except ProviderError as exc:
            print(f"Provider error: {exc}")
            return 1
        print(answer)
        return 0

    print(f"Agent: {config.name} ({config.agent_id})")
    if config.description:
        print(config.description)
    print("Type /help for commands. Type /exit to quit.\n")

    while True:
        try:
            user_input = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            return 0

        if not user_input:
            continue
        if user_input == "/exit":
            print("Bye.")
            return 0
        if user_input == "/help":
            _print_help(config.tools)
            continue
        if user_input.startswith("/tool"):
            try:
                output = Agent.handle_tool_command(user_input)
            except ToolError as exc:
                print(f"tool-error> {exc}")
            else:
                print(f"tool> {output}")
            continue

        try:
            answer = agent.respond(user_input, history=history)
        except ProviderError as exc:
            print(f"Provider error: {exc}")
            return 1

        print(f"agent> {answer}")
        history.append(ChatMessage(role="user", content=user_input))
        history.append(ChatMessage(role="assistant", content=answer))


def _cmd_list_tools(_: argparse.Namespace) -> int:
    for name in list_tool_names():
        print(name)
    return 0


def _print_help(enabled_tools: list[str]) -> None:
    print("Commands:")
    print("  /help                Show this help")
    print("  /tool <n> [arg]      Run a built-in tool directly")
    print("  /exit                Quit chat")
    print("\nEnabled tools:")
    print(describe_tools(enabled_tools))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="custom-agents",
        description="Create and run your own custom agents.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    create_cmd = sub.add_parser("create", help="Create a new agent JSON template")
    create_cmd.add_argument("agent_id", help="Unique id for your agent (e.g. support_bot)")
    create_cmd.add_argument("--name", help="Display name for your agent")
    create_cmd.add_argument(
        "--output",
        default=None,
        help="Output file path (default: agents/<agent_id>.json)",
    )
    create_cmd.set_defaults(func=_cmd_create)

    chat_cmd = sub.add_parser("chat", help="Chat with an agent config")
    chat_cmd.add_argument("config", help="Path to the agent JSON config")
    chat_cmd.add_argument("--message", help="Run a single prompt and exit")
    chat_cmd.set_defaults(func=_cmd_chat)

    tools_cmd = sub.add_parser("list-tools", help="List built-in tool names")
    tools_cmd.set_defaults(func=_cmd_list_tools)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "create" and args.output is None:
        args.output = str(Path("agents") / f"{args.agent_id}.json")
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
