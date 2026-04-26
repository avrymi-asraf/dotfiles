# Project-local agent system example

This is a non-activating example. It demonstrates the required way of working without creating platform config files in this repository.

## Rules

- Use project/workspace-local setup only.
- Do not use user/global settings for project behavior.
- Use placeholders for secrets and machine-specific paths.
- Do not assume unsupported platform details; link to official docs or mark unknowns.

## Example layout

```text
example-project/
  README.md
  skills/
    example-skill/
      SKILL.md              # source skill in this repo style
      mcp-server.py         # optional source MCP server script

  # OpenCode, only when intentionally activated:
  opencode.json
  AGENTS.md
  .opencode/agents/example.md
  .opencode/skills/example-skill/SKILL.md

  # VS Code / Copilot, only when intentionally activated:
  .github/copilot-instructions.md
  .github/instructions/example.instructions.md
  .github/prompts/example.prompt.md
  .github/agents/example.agent.md
  .github/skills/example-skill/SKILL.md
  .vscode/mcp.json

  # Codex, only when intentionally activated in a trusted project:
  AGENTS.override.md
  .codex/config.toml
  .agents/skills/example-skill/SKILL.md
```

## Placeholder MCP snippets

OpenCode project config shape:

```json
{
  "mcp": {
    "example-tool": {
      "type": "local",
      "command": ["uv", "run", "skills/example-skill/mcp-server.py"],
      "environment": {
        "EXAMPLE_TOKEN": "<set-outside-git>"
      }
    }
  }
}
```

VS Code workspace MCP shape:

```json
{
  "servers": {
    "example-tool": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "skills/example-skill/mcp-server.py"],
      "env": {
        "EXAMPLE_TOKEN": "<set-outside-git>"
      }
    }
  }
}
```

Codex trusted project config shape:

```toml
[mcp_servers.example-tool]
command = "uv"
args = ["run", "skills/example-skill/mcp-server.py"]

[mcp_servers.example-tool.env]
EXAMPLE_TOKEN = "<set-outside-git>"
```

## Agent memory pattern

If a project keeps local agent memory, document the convention next to the agent definitions. In this repository, `.opencode/agents/*.memory` is a repo convention, not verified official OpenCode memory behavior.

Keep memory project-scoped, concise, and free of secrets.
