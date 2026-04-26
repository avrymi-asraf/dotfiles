# PDF-to-Markdown MCP Implementation

## Source files

- MCP server: `skills/pdf-to-markdown-mcp/mcp-server.py`
- Companion skill documentation: `skills/pdf-to-markdown-mcp/SKILL.md`
- Tests: `skills/pdf-to-markdown-mcp/tests/test_mcp_server.py`

## Purpose

This implementation adds a local [[../concepts/pdf-to-markdown-mcp|PDF-to-Markdown MCP]] that converts local PDFs into Markdown using LLM vision providers. It emphasizes complete extraction of visible text, equations, mathematical symbols, tables, captions, footnotes, and reading order, with uniform equation formatting suitable for downstream Markdown use.

## Implementation conventions

- The server is a single PEP 723 `uv` Python script.
- It uses FastMCP and exposes `convert_pdf_to_markdown(...) -> str`.
- Successful calls return a JSON string containing `ok`, `provider`, `model`, `pdf_path`, `page_count`, `pages_converted`, `markdown`, `warnings`, and `stats`.
- Failures return a string beginning with `Error: ...`.
- Do not edit, copy, or expose secret values from `opencode.json` or any private config.
- Manual MCP registration must use placeholders only, never real credentials.

## Providers and configuration

- [[../entities/google-gemini|Google Gemini]] requires `GOOGLE_API_KEY`.
  - Optional `GEMINI_API_BASE_URL`.
  - Optional `PDF_TO_MD_GOOGLE_MODEL`; default: `gemini-2.5-flash`.
- [[../entities/ollama|Ollama]] uses a local service.
  - Optional `OLLAMA_BASE_URL`; default: `http://localhost:11434`.
  - Optional `PDF_TO_MD_OLLAMA_MODEL`; default: `llava:latest`.

## Quality features

- Uses both embedded PDF text and rendered page PNG images so the model can cross-check OCR/vision output.
- The extraction prompt requires exact reading order and forbids omission, invention, summarization, equation screenshots, or image placeholders for equations.
- It requires all visible text, headers, footers, labels, captions, marginalia, footnotes, references, annotations, equations, symbols, tables, units, row/column labels, and notes.
- Equations are normalized to inline `$...$`, display `$$...$$`, aligned `\begin{aligned} ... \end{aligned}`, and equation numbers with `\tag{}`.
- Simple rectangular tables use Markdown tables; complex or merged-cell tables use HTML.
- Optional `completeness_check` performs a second provider pass and appends provider-identified missing visible content under a completeness heading.

## Validation recorded

- Syntax check passed: `python3 -m py_compile 'skills/pdf-to-markdown-mcp/mcp-server.py'`.
- Targeted test command passed with 6 tests: `uv run --with pytest --with 'mcp[cli]>=1.2.0' --with 'httpx>=0.27.0' --with 'pymupdf>=1.24.0' pytest 'skills/pdf-to-markdown-mcp/tests/test_mcp_server.py'`.
- Tests cover page parsing/validation, prompt quality requirements, equation normalization outside code fences, Google payload construction, Ollama payload construction, and integration with a generated PDF plus mocked provider.

## Limitations and cautions

- Tests are mocked and deterministic; they do not verify live provider quality.
- Live extraction quality depends on the selected vision model.
- Password-protected PDFs are rejected.
- Very large PDFs may require page selection and/or `max_pages`.
- The completeness-check pass is useful but is not a mathematical guarantee of complete extraction.
- Secret values must not be copied into the wiki or committed configuration; use placeholder-only examples.

## Related wiki pages

- [[../concepts/pdf-to-markdown-mcp|PDF-to-Markdown MCP]]
- [[../entities/google-gemini|Google Gemini]]
- [[../entities/ollama|Ollama]]
