# Data Wiki Index

Catalog of persistent knowledge for this repository. Raw source files, when present, live under `data-place/raw/`; curated wiki knowledge lives here.

## Sources

- [PDF-to-Markdown MCP implementation](sources/pdf-to-markdown-mcp-implementation.md) — Completed local FastMCP server for converting PDFs to Markdown with Gemini or Ollama vision models, including test status and limitations.

## Concepts

- [PDF-to-Markdown MCP](concepts/pdf-to-markdown-mcp.md) — Architecture, configuration, conventions, quality contract, validation status, and operational limits for the PDF conversion MCP.

## Entities

- [Google Gemini](entities/google-gemini.md) — Cloud vision provider used by the PDF-to-Markdown MCP via `GOOGLE_API_KEY` and optional Gemini configuration.
- [Ollama](entities/ollama.md) — Local vision-provider option for the PDF-to-Markdown MCP with default local endpoint and model.
