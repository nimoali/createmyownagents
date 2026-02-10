import unittest

from custom_agents.tools import ToolError, run_builtin_tool


class ToolTests(unittest.TestCase):
    def test_calculator(self) -> None:
        result = run_builtin_tool("calculator", "(2 + 3) * 4")
        self.assertEqual(result, "20")

    def test_calculator_rejects_unsafe_expression(self) -> None:
        with self.assertRaises(ToolError):
            run_builtin_tool("calculator", "__import__('os').system('whoami')")

    def test_unknown_tool(self) -> None:
        with self.assertRaises(ToolError):
            run_builtin_tool("does_not_exist", "")


if __name__ == "__main__":
    unittest.main()
