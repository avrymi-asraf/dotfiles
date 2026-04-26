---
name: project-local-agent-systems
description: Build and document project-local agent, skill, MCP, and memory setups across OpenCode, VS Code/Copilot, and Codex without using user/global settings.
---

# Project-local agent systems

Use this skill when designing or documenting repository-local agents, skills, MCP servers, prompts, custom instructions, or agent memory. The default is always project/workspace-local setup only.

## Core rules

- Do not use user/global settings for project behavior.
- Do not commit secrets; use placeholders such as `<set-outside-git>`.
- Do not assume platform behavior that has not been verified in official docs.
- Do not create active platform directories/files unless the user explicitly approves them.
- Keep reusable source skills in this repo's `skills/<skill>/SKILL.md` convention unless activation in a platform-native path is intended.

## Repository conventions

- Source skills live at `skills/<skill>/SKILL.md`.
- Source MCP scripts can live beside a skill, commonly `skills/<skill>/mcp-server.py`.
- This repo has used `.opencode/agents/*.md` for active OpenCode agents.
- This repo has used `.opencode/agents/*.memory` as local agent memory, but official OpenCode memory support was not verified.

## Platform-local paths

### OpenCode

Verified project-local paths to document or use when approved:

- `opencode.json`
- `AGENTS.md`
- `.opencode/agents/*.md`
- `.opencode/skills/*/SKILL.md`
- local MCP entries in `opencode.json`

Use placeholder local MCP snippets only:

```json
{
  "mcp": {
    "example-tool": {
      "type": "local",
      "command": ["uv", "run", "skills/example-tool/mcp-server.py"],
      "environment": {
        "EXAMPLE_TOKEN": "<set-outside-git>"
      }
    }
  }
}
```

### VS Code / GitHub Copilot

Verified workspace-local paths to document or use when approved:

- `.github/copilot-instructions.md`
- `.github/instructions/**/*.instructions.md`
- `.github/prompts/**/*.prompt.md`
- `.github/agents/*.agent.md`
- `.github/skills/*/SKILL.md`
- `.vscode/mcp.json`

Use workspace MCP, not user settings:

```json
{
  "servers": {
    "example-tool": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "skills/example-tool/mcp-server.py"],
      "env": {
        "EXAMPLE_TOKEN": "<set-outside-git>"
      }
    }
  }
}
```

### OpenAI Codex

Verified project-local paths to document or use when approved:

- `AGENTS.md`
- `AGENTS.override.md`
- trusted `.codex/config.toml` with `[mcp_servers.<name>]`
- `.agents/skills/*/SKILL.md`

Only create `.codex/config.toml` in trusted projects when explicitly requested:

```toml
[mcp_servers.example-tool]
command = "uv"
args = ["run", "skills/example-tool/mcp-server.py"]

[mcp_servers.example-tool.env]
EXAMPLE_TOKEN = "<set-outside-git>"
```

## Documentation workflow

1. Identify the target platform and whether activation is approved.
2. If activation is not approved, write examples in docs only.
3. If activation is approved, create only the project-local files for that platform.
4. Keep snippets minimal and placeholder-only.
5. Link to official docs for config, agents, MCP, skills, and instruction files.
6. Mention unknowns explicitly instead of filling gaps with assumptions.

## Safety checklist

- No user/global config paths were edited.
- No unapproved active directories were created.
- No real tokens, account IDs, machine paths, or private endpoints were committed.
- Skill files have YAML frontmatter with `name` and `description`.
- Any memory convention is documented as project-local and, if applicable, unofficial.
