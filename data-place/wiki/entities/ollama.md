# Ollama

Ollama is the local vision-provider option supported by the [[../concepts/pdf-to-markdown-mcp|PDF-to-Markdown MCP]].

## Configuration in this repository

- Uses a local Ollama service with a vision model.
- Optional base URL: `OLLAMA_BASE_URL`.
- Default base URL: `http://localhost:11434`.
- Optional model override: `PDF_TO_MD_OLLAMA_MODEL`.
- Default model: `llava:latest`.

## Operational note

Live conversion quality depends on the installed local vision model. Very large PDFs should use page selection and/or `max_pages` to manage runtime.

## Related source

- [[../sources/pdf-to-markdown-mcp-implementation|PDF-to-Markdown MCP implementation]]
