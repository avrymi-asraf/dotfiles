# VS Code / GitHub Copilot

## Role in this repository

VS Code/GitHub Copilot is one of the platforms covered by the repository's project-local agent system documentation. The repo guidance requires workspace-local configuration for project behavior.

## Verified workspace-local paths

- `.github/copilot-instructions.md`.
- `.github/instructions/**/*.instructions.md`.
- `.github/prompts/**/*.prompt.md`.
- `.github/agents/*.agent.md`.
- `.github/skills/*/SKILL.md`.
- `.vscode/mcp.json` for workspace MCP servers.

## Safety notes

- Use `.vscode/mcp.json` for workspace MCP, not user settings.
- Keep credentials out of workspace files; use placeholders or environment variables.

## Sources and related pages

- [[Project-local agent systems|../concepts/project-local-agent-systems.md]]
- [[Project-local agent system documentation|../sources/project-local-agent-system-docs.md]]
- [`README.md`](../../../README.md)
- [`docs/project-local-agent-system-example.md`](../../../docs/project-local-agent-system-example.md)
