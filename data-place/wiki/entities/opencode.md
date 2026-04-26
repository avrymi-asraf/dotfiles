# OpenCode

## Role in this repository

OpenCode is one of the platforms covered by the repository's project-local agent system documentation. The repo guidance permits OpenCode setup only through project-local files, not user/global configuration.

## Verified project-local paths

- `opencode.json` — project configuration and local MCP entries.
- `AGENTS.md` — repository instructions/rules.
- `.opencode/agents/*.md` — project-local agent definitions.
- `.opencode/skills/*/SKILL.md` — OpenCode-native project-local skills.

## Safety notes

- Do not copy or expose real `opencode.json` values; they may contain secrets.
- Use placeholder-only MCP examples.
- `.opencode/agents/*.memory` is a repo convention for local memory, but official OpenCode memory support was not verified.

## Sources and related pages

- [[Project-local agent systems|../concepts/project-local-agent-systems.md]]
- [[Project-local agent system documentation|../sources/project-local-agent-system-docs.md]]
- [`README.md`](../../../README.md)
- [`skills/project-local-agent-systems/SKILL.md`](../../../skills/project-local-agent-systems/SKILL.md)
