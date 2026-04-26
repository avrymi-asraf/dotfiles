# OpenAI Codex

## Role in this repository

OpenAI Codex is one of the platforms covered by the repository's project-local agent system documentation. The repo guidance permits only trusted project-local Codex configuration when intentionally needed.

## Verified project-local paths

- `AGENTS.md`.
- `AGENTS.override.md`.
- Trusted `.codex/config.toml` with `[mcp_servers.<name>]`.
- `.agents/skills/*/SKILL.md`.

## Safety notes

- Do not create user/global Codex config for project behavior.
- Create `.codex/config.toml` only in trusted projects and only when explicitly requested.
- The current repository has `.codex` as an empty file, which conflicts with creating a `.codex/` directory unless a future approved task resolves it.
- Use placeholder-only MCP examples and keep credentials outside committed files.

## Sources and related pages

- [[Project-local agent systems|../concepts/project-local-agent-systems.md]]
- [[Project-local agent system documentation|../sources/project-local-agent-system-docs.md]]
- [`README.md`](../../../README.md)
- [`skills/project-local-agent-systems/SKILL.md`](../../../skills/project-local-agent-systems/SKILL.md)
