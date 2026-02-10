# createmyownagents

Create your own agents with a small Python framework:

- JSON-based agent configs
- OpenAI-compatible chat provider support
- Built-in tool system (`time`, `calculator`, `echo`)
- CLI to scaffold and chat with your agents

## Quick start

### 1) Create a virtual environment (optional)

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2) Install locally

```bash
python3 -m pip install -e .
```

### 3) Set your API key

```bash
export OPENAI_API_KEY="your_api_key_here"
```

### 4) Create your first agent config

```bash
python3 -m custom_agents create support_bot --name "Support Bot"
```

This creates:

```text
agents/support_bot.json
```

### 5) Customize your agent

Open `agents/support_bot.json` and edit:

- `system_prompt` (persona + behavior)
- `model`
- `tools`
- `temperature`

### 6) Chat with your agent

```bash
python3 -m custom_agents chat agents/support_bot.json
```

Single-message mode:

```bash
python3 -m custom_agents chat agents/support_bot.json --message "Give me a 3-step launch plan"
```

## Built-in tools

List available tool names:

```bash
python3 -m custom_agents list-tools
```

Default tools:

- `time` - current UTC timestamp
- `calculator` - safe arithmetic evaluation
- `echo` - returns your input

In interactive chat, you can run a tool manually:

```text
/tool calculator (2 + 3) * 4
```

## Agent config format

```json
{
  "agent_id": "example_assistant",
  "name": "Example Assistant",
  "description": "A friendly starter agent.",
  "system_prompt": "You are a concise, practical assistant.",
  "model": "gpt-4o-mini",
  "api_base": "https://api.openai.com/v1",
  "api_key_env": "OPENAI_API_KEY",
  "temperature": 0.2,
  "max_tokens": 400,
  "tools": ["time", "calculator", "echo"]
}
```

## OpenAI-compatible APIs

Point `api_base` to any OpenAI-compatible endpoint.
The runtime sends requests to:

```text
<api_base>/chat/completions
```

## Run tests

```bash
python3 -m unittest discover -s tests -v
```
