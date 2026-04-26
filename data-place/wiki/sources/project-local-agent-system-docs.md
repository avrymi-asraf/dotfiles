# Project-local agent system documentation

## Summary

This source captures the completed documentation task that updated the repository's project-local agent system guidance in [`README.md`](../../../README.md), [`docs/project-local-agent-system-example.md`](../../../docs/project-local-agent-system-example.md), and [`skills/project-local-agent-systems/SKILL.md`](../../../skills/project-local-agent-systems/SKILL.md). The stable rule across all three files is that reusable agent, skill, MCP, prompt, instruction, and memory setup for this repository must remain project/workspace-local, not user/global.

## Source files referenced

- [`README.md`](../../../README.md) — repo overview, platform path catalog, official documentation links, and safe workflow.
- [`docs/project-local-agent-system-example.md`](../../../docs/project-local-agent-system-example.md) — non-activating example layout and placeholder MCP snippets.
- [`skills/project-local-agent-systems/SKILL.md`](../../../skills/project-local-agent-systems/SKILL.md) — reusable skill for designing/documenting project-local agent systems across OpenCode, VS Code/Copilot, and Codex.

## Stable knowledge extracted

- The repository intentionally documents project/workspace-local configuration only; user/global settings, global MCP registries, and home-directory agent files are out of scope for project behavior.
- Committed documentation and config snippets must use placeholders such as `<set-outside-git>` and must not include real secrets, credentials, private endpoints, account IDs, or machine-specific paths.
- Official web research was required for platform-specific paths; unsupported or unverified platform behavior must be marked unknown rather than assumed.
- Top-level [`skills/<skill>/SKILL.md`](../../../skills/project-local-agent-systems/SKILL.md) and optional `skills/<skill>/mcp-server.py` are this repo's source patterns. Platform-native active install paths differ and should be created only when activation is intended and approved.
- [`docs/project-local-agent-system-example.md`](../../../docs/project-local-agent-system-example.md) is explicitly non-activating: it demonstrates layouts/snippets without creating active platform config files in this repository.

## Verified platform-local paths

### OpenCode

- `opencode.json` for project config, including local MCP entries.
- `AGENTS.md` for repository instructions/rules.
- `.opencode/agents/*.md` for project-local agent definitions.
- `.opencode/skills/*/SKILL.md` for OpenCode-native project-local skills.
- Local MCP entries live in `opencode.json`.

Safety notes:

- Do **not** copy or expose existing `opencode.json` values; they may contain secrets.
- `.opencode/agents/*.memory` is a repository convention for local agent memory, but official OpenCode memory support was not verified.

### VS Code / GitHub Copilot

- `.github/copilot-instructions.md`.
- `.github/instructions/**/*.instructions.md`.
- `.github/prompts/**/*.prompt.md`.
- `.github/agents/*.agent.md`.
- `.github/skills/*/SKILL.md`.
- `.vscode/mcp.json` for workspace MCP servers.

Safety notes:

- Use `.vscode/mcp.json` for workspace MCP, not user settings.
- Keep credentials out of the file; use placeholders or environment variables.

### OpenAI Codex

- `AGENTS.md`.
- `AGENTS.override.md`.
- Trusted `.codex/config.toml` with `[mcp_servers.<name>]`.
- `.agents/skills/*/SKILL.md`.

Safety notes:

- Create `.codex/config.toml` only in trusted projects and only when intentionally needed.
- The current repository has `.codex` as an empty file, which conflicts with creating a `.codex/` directory unless the file is intentionally removed/replaced in a future approved task.

## Cross-links

- Concept synthesis: [[Project-local agent systems|../concepts/project-local-agent-systems.md]]
- Platform entities: [[OpenCode|../entities/opencode.md]], [[VS Code / GitHub Copilot|../entities/vscode-github-copilot.md]], [[OpenAI Codex|../entities/openai-codex.md]]
