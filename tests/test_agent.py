import unittest

from custom_agents.agent import Agent
from custom_agents.config import AgentConfig
from custom_agents.providers import ChatMessage


class FakeProvider:
    def __init__(self, outputs: list[str]) -> None:
        self.outputs = outputs
        self.calls: list[list[ChatMessage]] = []

    def generate(self, messages: list[ChatMessage], _: AgentConfig) -> str:
        self.calls.append(messages[:])
        return self.outputs[len(self.calls) - 1]


class AgentTests(unittest.TestCase):
    def test_tool_call_loop(self) -> None:
        config = AgentConfig(
            agent_id="math_bot",
            name="Math Bot",
            system_prompt="Be helpful.",
            tools=["calculator"],
        )
        provider = FakeProvider(
            outputs=[
                "TOOL_CALL calculator | 2+3",
                "The result is 5.",
            ]
        )
        agent = Agent(config=config, provider=provider)

        response = agent.respond("What is 2+3?")
        self.assertEqual(response, "The result is 5.")
        self.assertEqual(len(provider.calls), 2)

    def test_unknown_tool_in_config_raises(self) -> None:
        config = AgentConfig(
            agent_id="bad_bot",
            name="Bad Bot",
            system_prompt="Be helpful.",
            tools=["missing_tool"],
        )
        with self.assertRaises(ValueError):
            Agent(config=config)


if __name__ == "__main__":
    unittest.main()
