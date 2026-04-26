# PDF-to-Markdown MCP

The PDF-to-Markdown MCP is a local FastMCP server located at `skills/pdf-to-markdown-mcp/mcp-server.py`, with companion operational guidance in `skills/pdf-to-markdown-mcp/SKILL.md` and tests in `skills/pdf-to-markdown-mcp/tests/test_mcp_server.py`.

## Role in the repository

Use this MCP when an agent needs to convert a local PDF into clean Markdown with high fidelity. The conversion contract prioritizes complete visible-content extraction: all text, equations, symbols, tables, captions, footnotes, references, annotations, and page reading order.

## Tool shape

- Server style: PEP 723 `uv` script using FastMCP.
- Tool: `convert_pdf_to_markdown(...) -> str`.
- Success format: JSON string with conversion metadata, Markdown, warnings, and stats.
- Failure format: `Error: ...`.

## Providers

- [[../entities/google-gemini|Google Gemini]] is the default cloud path and requires `GOOGLE_API_KEY`; optional `GEMINI_API_BASE_URL`; optional `PDF_TO_MD_GOOGLE_MODEL`, defaulting to `gemini-2.5-flash`.
- [[../entities/ollama|Ollama]] is the local path; optional `OLLAMA_BASE_URL`, defaulting to `http://localhost:11434`; optional `PDF_TO_MD_OLLAMA_MODEL`, defaulting to `llava:latest`.

## Extraction contract

The implementation sends each selected page with both embedded PDF text and rendered PNG page imagery. The prompt requires exact reading order, no invented content, no summarized substitutions, `[illegible]` for unreadable visible content, and preservation of table captions/notes/units and equation numbers.

Equation formatting is normalized as follows:

- Inline math: `$...$`.
- Display math: `$$...$$` blocks.
- Aligned display math: `\begin{aligned} ... \end{aligned}` inside display math.
- Equation numbers: `\tag{}` where present.
- Avoid `\(...\)`, `\[...\]`, screenshots, and image placeholders for equations.

Tables use Markdown for simple rectangular structures and HTML for complex or merged-cell structures.

## Operational conventions

- Manual MCP registration should use placeholder credential values only.
- Do not edit, copy, or expose secret values from `opencode.json` or other private configuration.
- Use page selection and `max_pages` for very large PDFs to control runtime and cost.
- Use `completeness_check` when a second provider review is worth the added latency/cost; it appends possible missing content but is not a proof of completeness.

## Validation state

- Syntax check passed with `python3 -m py_compile 'skills/pdf-to-markdown-mcp/mcp-server.py'`.
- Targeted tests passed: 6 passed via `uv run --with pytest --with 'mcp[cli]>=1.2.0' --with 'httpx>=0.27.0' --with 'pymupdf>=1.24.0' pytest 'skills/pdf-to-markdown-mcp/tests/test_mcp_server.py'`.
- Current tests mock provider calls, so live provider quality remains model-dependent.

## Source summary

See [[../sources/pdf-to-markdown-mcp-implementation|PDF-to-Markdown MCP implementation]].
