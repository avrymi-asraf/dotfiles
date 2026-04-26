# dotfiles

Project-local agent, skill, and MCP examples for this repository.

This repository intentionally uses workspace/project-local configuration only. Do **not** put examples from this repository into user/global settings. Keep secrets out of committed files and use placeholders in documentation.

## What is in this repo

- `skills/<skill>/SKILL.md` — source-controlled skill documentation used by this repo.
- `skills/<skill>/mcp-server.py` — source-controlled MCP server scripts when a skill includes one.
- `docs/project-local-agent-system-example.md` — a non-activating example of project-local layouts and snippets.

Some platforms use different native install paths for active skills or agents. Treat this repo's top-level `skills/` directory as source material unless a platform-specific project-local path is intentionally created in that project.

## Project-local setup guide

Use project/workspace files only. Do not use user settings, global MCP registries, or home-directory agent files for reusable project behavior.

### OpenCode

Project-local paths to use when a project needs them:

- `opencode.json` — project config, including local MCP entries.
- `AGENTS.md` — repository instructions/rules.
- `.opencode/agents/*.md` — project-local agent definitions.
- `.opencode/skills/*/SKILL.md` — OpenCode-native project-local skills.
- `.opencode/agents/*.memory` — this repository's local memory convention; official memory support was not verified.

Local MCP entries should reference committed scripts with placeholders only, for example:

```json
{
  "mcp": {
    "example-tool": {
      "type": "local",
      "command": ["uv", "run", "skills/example-tool/mcp-server.py"],
      "environment": {
        "EXAMPLE_API_KEY": "<set-outside-git>"
      }
    }
  }
}
```

### VS Code / GitHub Copilot

Project/workspace-local paths to use when a project needs them:

- `.github/copilot-instructions.md`
- `.github/instructions/**/*.instructions.md`
- `.github/prompts/**/*.prompt.md`
- `.github/agents/*.agent.md`
- `.github/skills/*/SKILL.md`
- `.vscode/mcp.json`

Use `.vscode/mcp.json` for workspace MCP servers, not user settings. Keep credentials out of the file and use placeholders or environment variables.

### OpenAI Codex

Project-local paths to use when a project needs them:

- `AGENTS.md`
- `AGENTS.override.md`
- trusted `.codex/config.toml` with `[mcp_servers.<name>]`
- `.agents/skills/*/SKILL.md`

Only create a project `.codex/config.toml` when the project is trusted and intentionally needs Codex-local configuration. Do not create user/global Codex config for project behavior.

## Documentation links

OpenCode:

- Config: <https://opencode.ai/docs/config/>
- Agents: <https://opencode.ai/docs/agents/>
- Rules: <https://opencode.ai/docs/rules/>
- MCP: <https://opencode.ai/docs/mcp/>
- Skills: <https://opencode.ai/docs/skills/>

VS Code / GitHub Copilot:

- Copilot customization: <https://code.visualstudio.com/docs/copilot/copilot-customization>
- Custom instructions: <https://code.visualstudio.com/docs/copilot/copilot-customization#_custom-instructions>
- Prompt files: <https://code.visualstudio.com/docs/copilot/copilot-customization#_prompt-files-experimental>
- Custom agents: <https://code.visualstudio.com/docs/copilot/copilot-customization#_custom-chat-modes>
- Agent skills: <https://code.visualstudio.com/docs/copilot/copilot-customization#_agent-skills>
- MCP: <https://code.visualstudio.com/docs/copilot/chat/mcp-servers>

OpenAI Codex:

- Codex CLI: <https://github.com/openai/codex>
- Config: <https://github.com/openai/codex/blob/main/docs/config.md>
- AGENTS.md: <https://agents.md/>
- MCP: <https://github.com/openai/codex/blob/main/docs/config.md#mcp_servers>
- Skills: <https://github.com/openai/codex/blob/main/docs/skills.md>

## Safe workflow

1. Decide which platform needs project-local behavior.
2. Add or update only that platform's project/workspace files.
3. Use placeholder snippets in committed docs and configs; never commit real secrets.
4. Put reusable skill source in `skills/<skill>/SKILL.md`; copy or adapt it to a platform-native project-local skill path only when activation is intended.
5. Document any repo-local memory convention explicitly, especially when official platform support is unknown.
