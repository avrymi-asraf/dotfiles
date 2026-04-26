#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "mcp[cli]>=1.2.0",
#   "httpx>=0.27.0",
#   "pymupdf>=1.24.0",
# ]
# ///

from __future__ import annotations

import base64
import json
import os
import re
from pathlib import Path
from typing import Any

import fitz
import httpx
from mcp.server.fastmcp import FastMCP

DEFAULT_GOOGLE_MODEL = "gemini-2.5-flash"
DEFAULT_GOOGLE_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
DEFAULT_OLLAMA_MODEL = "llava:latest"
DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
MIN_DPI = 72
MAX_DPI = 300
DEFAULT_TIMEOUT = 120.0
MAX_ALLOWED_PAGES = 200

mcp = FastMCP(
    "pdf-to-markdown",
    instructions=(
        "Convert PDFs to Markdown with Google Gemini or Ollama vision models. "
        "The tool extracts visible text, equations, tables, captions, and footnotes "
        "while normalizing equations to consistent Markdown/LaTeX delimiters."
    ),
)


# -- Validation and PDF helpers ------------------------------------------------

def _validate_pdf_path(pdf_path: str) -> Path:
    path = Path(pdf_path or "").expanduser().resolve()
    if not path.exists():
        raise ValueError(f"pdf_path does not exist: {path}")
    if not path.is_file():
        raise ValueError(f"pdf_path is not a file: {path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError("pdf_path must point to a .pdf file")
    return path


def _validate_provider(provider: str) -> str:
    clean = (provider or "").strip().lower()
    if clean not in {"google", "ollama"}:
        raise ValueError("provider must be 'google' or 'ollama'")
    return clean


def _validate_dpi(render_dpi: int) -> int:
    if not isinstance(render_dpi, int) or not MIN_DPI <= render_dpi <= MAX_DPI:
        raise ValueError(f"render_dpi must be an integer between {MIN_DPI} and {MAX_DPI}")
    return render_dpi


def _validate_timeout(timeout_seconds: float | None) -> float:
    if timeout_seconds is None:
        return DEFAULT_TIMEOUT
    timeout = float(timeout_seconds)
    if timeout <= 0 or timeout > 900:
        raise ValueError("timeout_seconds must be > 0 and <= 900")
    return timeout


def _validate_max_pages(max_pages: int | None) -> int | None:
    if max_pages is None:
        return None
    if not isinstance(max_pages, int) or max_pages <= 0 or max_pages > MAX_ALLOWED_PAGES:
        raise ValueError(f"max_pages must be between 1 and {MAX_ALLOWED_PAGES}")
    return max_pages


def _open_pdf(path: Path) -> fitz.Document:
    try:
        doc = fitz.open(path)
    except Exception as exc:  # PyMuPDF raises several concrete exceptions.
        raise ValueError(f"Could not open PDF: {exc}") from exc
    if doc.needs_pass:
        doc.close()
        raise ValueError("Encrypted/password-protected PDFs are not supported")
    if doc.page_count < 1:
        doc.close()
        raise ValueError("PDF contains no pages")
    return doc


def _parse_pages(pages: str | None, page_count: int, max_pages: int | None = None) -> list[int]:
    if page_count < 1:
        raise ValueError("page_count must be positive")
    if pages is None or not pages.strip():
        selected = list(range(1, page_count + 1))
    else:
        selected: list[int] = []
        for raw_part in pages.split(","):
            part = raw_part.strip()
            if not part:
                raise ValueError("pages contains an empty selector")
            if "-" in part:
                bits = [b.strip() for b in part.split("-", 1)]
                if len(bits) != 2 or not all(b.isdigit() for b in bits):
                    raise ValueError(f"Invalid page range: {part}")
                start, end = int(bits[0]), int(bits[1])
                if start > end:
                    raise ValueError(f"Invalid descending page range: {part}")
                selected.extend(range(start, end + 1))
            else:
                if not part.isdigit():
                    raise ValueError(f"Invalid page selector: {part}")
                selected.append(int(part))
    if any(p < 1 or p > page_count for p in selected):
        raise ValueError(f"pages must be within 1..{page_count}")
    deduped = list(dict.fromkeys(selected))
    if max_pages is not None and len(deduped) > max_pages:
        raise ValueError(f"Selected {len(deduped)} pages but max_pages is {max_pages}")
    return deduped


def _page_payloads(doc: fitz.Document, selected_pages: list[int], render_dpi: int) -> list[dict[str, Any]]:
    zoom = render_dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)
    payloads: list[dict[str, Any]] = []
    for page_number in selected_pages:
        page = doc.load_page(page_number - 1)
        embedded_text = page.get_text("text") or ""
        pixmap = page.get_pixmap(matrix=matrix, alpha=False)
        png_bytes = pixmap.tobytes("png")
        payloads.append(
            {
                "page_number": page_number,
                "embedded_text": embedded_text,
                "image_mime_type": "image/png",
                "image_base64": base64.b64encode(png_bytes).decode("ascii"),
            }
        )
    return payloads


# -- Prompt construction -------------------------------------------------------

def _build_extraction_prompt(page_payloads: list[dict[str, Any]], extra_instructions: str | None = None) -> str:
    page_list = ", ".join(str(p["page_number"]) for p in page_payloads)
    embedded = []
    for payload in page_payloads:
        text = (payload.get("embedded_text") or "").strip()
        embedded.append(f"Page {payload['page_number']} embedded text:\n{text if text else '[no embedded text]'}")
    prompt = f"""
You are converting PDF page images to Markdown. Convert exactly pages: {page_list}.

Strict extraction contract:
- Extract all visible text in exact reading order: headings, body text, headers, footers, captions, labels, marginalia, footnotes, references, and annotations.
- Extract all equations and mathematical symbols. Do not omit, summarize, or replace equations with image placeholders.
- Do not invent content and do not summarize. If visible content is unreadable, write [illegible] at that position.
- Preserve lists, indentation cues, captions, cross references, equation numbers, table notes, and footnotes.

Uniform equation style (mandatory):
- Inline equations must use dollar delimiters only, like `$a+b=c$`.
- Display equations must be standalone `$$...$$` blocks with one blank line before and after.
- Multi-line/aligned equations must use `\\begin{{aligned}} ... \\end{{aligned}}` inside `$$...$$`.
- Preserve equation numbers with `\\tag{{...}}` when present.
- Never use `\\(...\\)`, `\\[...\\]`, Markdown image placeholders, or screenshots for equations.

Table rules:
- Use Markdown tables for simple rectangular tables.
- Use HTML tables for complex tables with merged cells, multi-row headers, or layout that Markdown cannot faithfully preserve.
- Preserve table captions, footnotes, units, row/column labels, and notes.

Return only Markdown for the requested pages. No commentary.

Embedded text for cross-checking OCR/vision output:
{chr(10).join(embedded)}
""".strip()
    if extra_instructions and extra_instructions.strip():
        prompt += "\n\nAdditional user instructions (do not override the strict extraction contract):\n"
        prompt += extra_instructions.strip()
    return prompt


def _build_completeness_prompt(markdown: str, page_payloads: list[dict[str, Any]]) -> str:
    return (
        _build_extraction_prompt(page_payloads)
        + "\n\nReview the draft Markdown below against the same page images and embedded text. "
        + "Return only missing visible content that should be appended, using the same equation/table rules. "
        + "If nothing is missing, return an empty response.\n\nDraft Markdown:\n"
        + markdown
    )


# -- Provider calls ------------------------------------------------------------

def _google_model(model: str | None) -> str:
    return (model or os.getenv("PDF_TO_MD_GOOGLE_MODEL") or DEFAULT_GOOGLE_MODEL).strip()


def _ollama_model(model: str | None) -> str:
    return (model or os.getenv("PDF_TO_MD_OLLAMA_MODEL") or DEFAULT_OLLAMA_MODEL).strip()


def _call_google(prompt: str, page_payloads: list[dict[str, Any]], model: str, timeout: float) -> str:
    api_key = os.getenv("GOOGLE_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("Missing GOOGLE_API_KEY environment variable")
    base_url = os.getenv("GEMINI_API_BASE_URL", DEFAULT_GOOGLE_BASE_URL).rstrip("/")
    url = f"{base_url}/models/{model}:generateContent"
    parts: list[dict[str, Any]] = [{"text": prompt}]
    for payload in page_payloads:
        parts.append(
            {
                "inline_data": {
                    "mime_type": payload["image_mime_type"],
                    "data": payload["image_base64"],
                }
            }
        )
    body = {"contents": [{"role": "user", "parts": parts}]}
    headers = {"x-goog-api-key": api_key, "content-type": "application/json"}
    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.post(url, headers=headers, json=body)
    except httpx.HTTPError as exc:
        raise RuntimeError(f"Google request failed: {exc}") from exc
    if response.status_code >= 400:
        raise RuntimeError(f"Google API error {response.status_code}: {response.text.strip()}")
    try:
        data = response.json()
        parts_out = data["candidates"][0]["content"].get("parts", [])
        text = "".join(part.get("text", "") for part in parts_out)
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Google API returned an unexpected response: {exc}") from exc
    return text.strip()


def _call_ollama(prompt: str, page_payloads: list[dict[str, Any]], model: str, timeout: float) -> str:
    base_url = os.getenv("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL).rstrip("/")
    url = f"{base_url}/api/generate"
    body = {
        "model": model,
        "prompt": prompt,
        "images": [payload["image_base64"] for payload in page_payloads],
        "stream": False,
    }
    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.post(url, json=body)
    except httpx.HTTPError as exc:
        raise RuntimeError(f"Ollama request failed: {exc}") from exc
    if response.status_code >= 400:
        raise RuntimeError(f"Ollama API error {response.status_code}: {response.text.strip()}")
    try:
        data = response.json()
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Ollama returned invalid JSON: {exc}") from exc
    text = data.get("response")
    if not isinstance(text, str):
        raise RuntimeError("Ollama response did not include a text response")
    return text.strip()


def _generate(provider: str, prompt: str, page_payloads: list[dict[str, Any]], model: str, timeout: float) -> str:
    if provider == "google":
        return _call_google(prompt, page_payloads, model, timeout)
    if provider == "ollama":
        return _call_ollama(prompt, page_payloads, model, timeout)
    raise ValueError(f"Unsupported provider: {provider}")


# -- Markdown post-processing --------------------------------------------------

def _split_fenced_code(markdown: str) -> list[tuple[bool, str]]:
    parts: list[tuple[bool, str]] = []
    pos = 0
    pattern = re.compile(r"(^```.*?$.*?^```\s*$)", re.MULTILINE | re.DOTALL)
    for match in pattern.finditer(markdown):
        if match.start() > pos:
            parts.append((False, markdown[pos : match.start()]))
        parts.append((True, match.group(1)))
        pos = match.end()
    if pos < len(markdown):
        parts.append((False, markdown[pos:]))
    return parts


def _normalize_equations(markdown: str) -> str:
    def normalize_text(text: str) -> str:
        text = re.sub(r"\\\((.+?)\\\)", lambda m: f"${m.group(1).strip()}$", text, flags=re.DOTALL)
        text = re.sub(r"\\\[(.+?)\\\]", lambda m: f"\n\n$${m.group(1).strip()}$$\n\n", text, flags=re.DOTALL)
        text = re.sub(r"\n{3,}(\$\$)", r"\n\n\1", text)
        text = re.sub(r"(\$\$)\n{3,}", r"\1\n\n", text)
        return text

    return "".join(segment if is_code else normalize_text(segment) for is_code, segment in _split_fenced_code(markdown))


def _cleanup_markdown_tables(markdown: str) -> str:
    lines = markdown.splitlines()
    cleaned: list[str] = []
    separator_re = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$")
    for line in lines:
        if separator_re.match(line):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            cleaned.append("| " + " | ".join(cells) + " |")
        else:
            cleaned.append(line.rstrip())
    return "\n".join(cleaned)


def _remove_duplicate_boundaries(chunks: list[str]) -> list[str]:
    if not chunks:
        return []
    merged = [chunks[0].strip()]
    for chunk in chunks[1:]:
        clean = chunk.strip()
        prev_lines = [l.strip() for l in merged[-1].splitlines() if l.strip()]
        curr_lines = [l.strip() for l in clean.splitlines() if l.strip()]
        if prev_lines and curr_lines and prev_lines[-1] == curr_lines[0] and len(curr_lines[0]) > 20:
            clean = "\n".join(clean.splitlines()[1:]).strip()
        merged.append(clean)
    return merged


def _postprocess(markdown: str) -> str:
    text = _normalize_equations(markdown.strip())
    text = _cleanup_markdown_tables(text)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip() + "\n"


def _merge_pages(page_markdown: list[tuple[int, str]], include_page_markers: bool) -> str:
    chunks: list[str] = []
    for page_number, markdown in page_markdown:
        body = markdown.strip()
        if include_page_markers:
            body = f"<!-- Page {page_number} -->\n\n{body}"
        chunks.append(body)
    return _postprocess("\n\n".join(_remove_duplicate_boundaries(chunks)))


# -- MCP Tool ------------------------------------------------------------------

@mcp.tool()
def convert_pdf_to_markdown(
    pdf_path: str,
    provider: str = "google",
    model: str | None = None,
    pages: str | None = None,
    include_page_markers: bool = True,
    completeness_check: bool = False,
    render_dpi: int = 180,
    max_pages: int | None = None,
    timeout_seconds: float | None = None,
    extra_instructions: str | None = None,
) -> str:
    """Convert selected PDF pages to Markdown using Google Gemini or Ollama."""
    try:
        clean_provider = _validate_provider(provider)
        dpi = _validate_dpi(render_dpi)
        timeout = _validate_timeout(timeout_seconds)
        page_limit = _validate_max_pages(max_pages)
        path = _validate_pdf_path(pdf_path)
        selected_model = _google_model(model) if clean_provider == "google" else _ollama_model(model)
        warnings: list[str] = []

        doc = _open_pdf(path)
        pdf_page_count = doc.page_count
        try:
            selected_pages = _parse_pages(pages, pdf_page_count, page_limit)
            page_markdown: list[tuple[int, str]] = []
            total_embedded_chars = 0
            for page_number in selected_pages:
                payloads = _page_payloads(doc, [page_number], dpi)
                total_embedded_chars += len(payloads[0].get("embedded_text") or "")
                prompt = _build_extraction_prompt(payloads, extra_instructions)
                markdown = _generate(clean_provider, prompt, payloads, selected_model, timeout)
                if not markdown:
                    warnings.append(f"Provider returned empty Markdown for page {page_number}")
                page_markdown.append((page_number, markdown))
        finally:
            doc.close()

        merged = _merge_pages(page_markdown, include_page_markers)
        if completeness_check:
            doc = _open_pdf(path)
            try:
                all_payloads = _page_payloads(doc, selected_pages, dpi)
            finally:
                doc.close()
            additions = _generate(
                clean_provider,
                _build_completeness_prompt(merged, all_payloads),
                all_payloads,
                selected_model,
                timeout,
            ).strip()
            if additions:
                merged = _postprocess(merged + "\n\n## Completeness check additions\n\n" + additions)
                warnings.append("Completeness check returned additional content appended at end")

        result = {
            "ok": True,
            "provider": clean_provider,
            "model": selected_model,
            "pdf_path": str(path),
            "page_count": pdf_page_count,
            "pages_converted": selected_pages,
            "markdown": merged,
            "warnings": warnings,
            "stats": {
                "render_dpi": dpi,
                "embedded_text_chars": total_embedded_chars,
                "markdown_chars": len(merged),
                "completeness_check": completeness_check,
            },
        }
        return json.dumps(result, indent=2)
    except Exception as exc:
        return f"Error: {exc}"


if __name__ == "__main__":
    mcp.run()
