import json
import tempfile
import unittest
from pathlib import Path

from custom_agents.config import AgentConfig, create_agent_template, load_agent_config


class ConfigTests(unittest.TestCase):
    def test_template_round_trip(self) -> None:
        payload = create_agent_template("support_bot", name="Support Bot")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "support_bot.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            config = load_agent_config(path)

        self.assertEqual(config.agent_id, "support_bot")
        self.assertEqual(config.name, "Support Bot")
        self.assertIn("system_prompt", payload)

    def test_validation_missing_fields(self) -> None:
        with self.assertRaises(ValueError):
            AgentConfig.from_dict({"name": "No Id"})


if __name__ == "__main__":
    unittest.main()
