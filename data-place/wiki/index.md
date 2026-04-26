# Data Wiki Index

Catalog of persistent knowledge for this repository. Raw source files, when present, live under `data-place/raw/`; curated wiki knowledge lives here.

## Sources

- [Project-local agent system documentation](sources/project-local-agent-system-docs.md) — Stable project/workspace-local agent, skill, MCP, prompt, and memory guidance across OpenCode, VS Code/Copilot, and Codex, with safety caveats.
- [PDF-to-Markdown MCP implementation](sources/pdf-to-markdown-mcp-implementation.md) — Completed local FastMCP server for converting PDFs to Markdown with Gemini or Ollama vision models, including test status and limitations.

## Concepts

- [Project-local agent systems](concepts/project-local-agent-systems.md) — Repository rule and platform path synthesis for project-local-only agent systems, including source-vs-native path distinctions and secret-safety constraints.
- [PDF-to-Markdown MCP](concepts/pdf-to-markdown-mcp.md) — Architecture, configuration, conventions, quality contract, validation status, and operational limits for the PDF conversion MCP.

## Entities

- [Google Gemini](entities/google-gemini.md) — Cloud vision provider used by the PDF-to-Markdown MCP via `GOOGLE_API_KEY` and optional Gemini configuration.
- [Ollama](entities/ollama.md) — Local vision-provider option for the PDF-to-Markdown MCP with default local endpoint and model.
- [OpenAI Codex](entities/openai-codex.md) — Platform with project-local `AGENTS.md`, `AGENTS.override.md`, trusted `.codex/config.toml` MCP entries, and `.agents/skills/*/SKILL.md` support.
- [OpenCode](entities/opencode.md) — Platform with project-local `opencode.json`, `AGENTS.md`, `.opencode/agents/*.md`, `.opencode/skills/*/SKILL.md`, and local MCP entries.
- [VS Code / GitHub Copilot](entities/vscode-github-copilot.md) — Platform with workspace-local Copilot instructions/prompts/agents/skills and `.vscode/mcp.json` MCP configuration.
