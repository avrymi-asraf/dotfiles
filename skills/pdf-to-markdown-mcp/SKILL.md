---
name: pdf-to-markdown-mcp
description: Local MCP server that converts PDFs to Markdown with Google Gemini or Ollama vision models, emphasizing complete text, equation, and table extraction with uniform equation formatting.
---

# PDF to Markdown MCP

Use this MCP when a user needs a PDF converted into clean Markdown using a multimodal LLM. It is designed for visible text, equations, tables, captions, footnotes, and reading-order preservation.

## Files

- `skills/pdf-to-markdown-mcp/mcp-server.py`
- `skills/pdf-to-markdown-mcp/tests/`

## Requirements

The server is a single executable `uv`/PEP 723 Python script. Dependencies are declared inline:

- `mcp[cli]>=1.2.0`
- `httpx>=0.27.0`
- `pymupdf>=1.24.0`

Provider environment variables:

| Provider | Required | Optional |
| --- | --- | --- |
| Google | `GOOGLE_API_KEY` | `GEMINI_API_BASE_URL`, `PDF_TO_MD_GOOGLE_MODEL` |
| Ollama | local Ollama service with a vision model | `OLLAMA_BASE_URL`, `PDF_TO_MD_OLLAMA_MODEL` |

Defaults:

- Google model: `gemini-2.5-flash`
- Ollama model: `llava:latest`
- Ollama base URL: `http://localhost:11434`

## Run Manually

```bash
uv run skills/pdf-to-markdown-mcp/mcp-server.py
```

Do not start the server just to run unit tests; tests import helpers and mock provider calls.

## Manual MCP Registration

Add a local MCP entry to your private config with placeholders only. Do not commit real secrets.

```json
{
  "mcp": {
    "pdf-to-markdown": {
      "type": "local",
      "command": ["uv", "run", "skills/pdf-to-markdown-mcp/mcp-server.py"],
      "enabled": true,
      "environment": {
        "GOOGLE_API_KEY": "<your-google-api-key>",
        "PDF_TO_MD_GOOGLE_MODEL": "gemini-2.5-flash",
        "OLLAMA_BASE_URL": "http://localhost:11434",
        "PDF_TO_MD_OLLAMA_MODEL": "llava:latest"
      }
    }
  }
}
```

## Tool

`convert_pdf_to_markdown(...) -> str`

Parameters:

- `pdf_path: str` — local PDF path.
- `provider: str = "google"` — `google` or `ollama`.
- `model: str | None = None` — override provider default model.
- `pages: str | None = None` — `1`, `1-3`, or `1,3,5-7`; default is all pages.
- `include_page_markers: bool = True` — inserts `<!-- Page N -->` markers.
- `completeness_check: bool = False` — optional second provider pass that appends missing visible content under a heading.
- `render_dpi: int = 180` — page image render DPI; valid range is 72..300.
- `max_pages: int | None = None` — sanity limit for selected pages.
- `timeout_seconds: float | None = None` — provider call timeout.
- `extra_instructions: str | None = None` — additional instructions that cannot override the extraction contract.

Success returns a JSON string with `ok`, `provider`, `model`, `pdf_path`, `page_count`, `pages_converted`, `markdown`, `warnings`, and `stats`. Failures return `Error: ...`.

## Extraction Contract

The prompt requires:

- all visible text in exact reading order;
- headings, body text, headers, footers, captions, labels, marginalia, footnotes, references, and annotations;
- all equations and mathematical symbols;
- no invented or summarized content;
- `[illegible]` where visible content cannot be read;
- table captions, footnotes, units, row/column labels, and notes.

Equation style is normalized to:

- inline math: `$...$` only;
- display math: `$$...$$` blocks with a blank line before and after;
- aligned display math: `\begin{aligned} ... \end{aligned}` inside `$$...$$`;
- equation numbers: `\tag{...}` where appropriate;
- never `\(...\)`, `\[...\]`, or image placeholders for equations.

Tables use Markdown for simple rectangular tables and HTML for complex or merged-cell tables.

## Testing Guidance

Tests live in `skills/pdf-to-markdown-mcp/tests/` and are deterministic. Provider HTTP calls are mocked; tests should not require live Google or Ollama services.

Suggested formal test command for the next validation step:

```bash
uv run --with pytest --with 'mcp[cli]>=1.2.0' --with 'httpx>=0.27.0' --with 'pymupdf>=1.24.0' pytest skills/pdf-to-markdown-mcp/tests
```

## Limitations

- Conversion quality depends on the selected vision model.
- Very large PDFs should be processed with `pages` and `max_pages` to control runtime/cost.
- Password-protected PDFs are rejected.
- The completeness check can only append provider-identified missing content; it must not invent content.
