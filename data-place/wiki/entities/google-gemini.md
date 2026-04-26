# Google Gemini

Google Gemini is the cloud vision provider supported by the [[../concepts/pdf-to-markdown-mcp|PDF-to-Markdown MCP]].

## Configuration in this repository

- Required environment variable: `GOOGLE_API_KEY`.
- Optional environment variable: `GEMINI_API_BASE_URL`.
- Optional model override: `PDF_TO_MD_GOOGLE_MODEL`.
- Default model: `gemini-2.5-flash`.

## Security note

Never copy real API key values into wiki pages, examples, commits, or MCP registration snippets. Use placeholders only, and do not extract secrets from `opencode.json`.

## Related source

- [[../sources/pdf-to-markdown-mcp-implementation|PDF-to-Markdown MCP implementation]]
