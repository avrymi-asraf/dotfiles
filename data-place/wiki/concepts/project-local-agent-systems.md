# Project-local agent systems

## Definition

A project-local agent system keeps agent instructions, skills, MCP server registrations, prompts, and memory conventions inside the repository/workspace that owns the behavior. In this repository, the rule is explicit: use project/workspace-local files only and do not rely on user/global settings for reusable project behavior.

## Safety rule

- Do not commit secrets or real credential values.
- Use placeholders such as `<set-outside-git>` in examples.
- Do not copy existing `opencode.json` values into documentation or wiki pages because they may contain secrets.
- Do not create active platform directories/files unless the user explicitly approves activation.
- Link to official docs or mark unknowns; do not infer unsupported platform behavior.

## Repository source convention vs platform-native paths

This repo keeps reusable skill source at `skills/<skill>/SKILL.md`; if a skill has an MCP helper, the source script may live at `skills/<skill>/mcp-server.py`. These source paths are not automatically the same as active platform-native install paths.

When activation is intended, platform-specific project-local paths differ:

- [[OpenCode|../entities/opencode.md]] uses `opencode.json`, `AGENTS.md`, `.opencode/agents/*.md`, `.opencode/skills/*/SKILL.md`, and local MCP entries in `opencode.json`.
- [[VS Code / GitHub Copilot|../entities/vscode-github-copilot.md]] uses `.github/copilot-instructions.md`, `.github/instructions/**/*.instructions.md`, `.github/prompts/**/*.prompt.md`, `.github/agents/*.agent.md`, `.github/skills/*/SKILL.md`, and `.vscode/mcp.json`.
- [[OpenAI Codex|../entities/openai-codex.md]] uses `AGENTS.md`, `AGENTS.override.md`, trusted `.codex/config.toml` with `[mcp_servers.<name>]`, and `.agents/skills/*/SKILL.md`.

## Non-activating documentation pattern

[`docs/project-local-agent-system-example.md`](../../../docs/project-local-agent-system-example.md) demonstrates layouts and placeholder MCP snippets without creating active platform configuration in this repository. This is the preferred pattern when documenting capabilities but not enabling them.

## Current repository caveats

- `.opencode/agents/*.memory` is a repository-local memory convention, not verified official OpenCode memory behavior.
- The current `.codex` path is an empty file and therefore conflicts with creating `.codex/config.toml` as a directory path unless a future approved change resolves that filesystem conflict.

## Sources

- [[Project-local agent system documentation|../sources/project-local-agent-system-docs.md]]
- [`README.md`](../../../README.md)
- [`docs/project-local-agent-system-example.md`](../../../docs/project-local-agent-system-example.md)
- [`skills/project-local-agent-systems/SKILL.md`](../../../skills/project-local-agent-systems/SKILL.md)
