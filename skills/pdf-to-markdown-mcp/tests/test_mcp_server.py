from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import fitz


SERVER_PATH = Path(__file__).resolve().parents[1] / "mcp-server.py"


def load_server():
    spec = importlib.util.spec_from_file_location("pdf_to_markdown_mcp_server", SERVER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def make_pdf(path: Path, text: str = "Equation: E = mc^2") -> Path:
    doc = fitz.open()
    page = doc.new_page(width=300, height=200)
    page.insert_text((36, 72), text)
    doc.save(path)
    doc.close()
    return path


def test_parse_pages_and_validation_bounds():
    server = load_server()
    assert server._parse_pages(None, 5) == [1, 2, 3, 4, 5]
    assert server._parse_pages("1,3,5", 5) == [1, 3, 5]
    assert server._parse_pages("1-3,3,5", 5) == [1, 2, 3, 5]

    for selector in ("0", "6", "3-1", "1,,2", "x"):
        try:
            server._parse_pages(selector, 5)
        except ValueError:
            pass
        else:
            raise AssertionError(f"selector should fail: {selector}")


def test_prompt_contains_strict_equation_table_all_text_rules():
    server = load_server()
    prompt = server._build_extraction_prompt(
        [{"page_number": 1, "embedded_text": "Table 1 and equation", "image_base64": "abc"}],
        "Preserve line breaks.",
    )
    assert "Extract all visible text" in prompt
    assert "exact reading order" in prompt
    assert "Extract all equations" in prompt
    assert "Inline equations must use dollar delimiters" in prompt
    assert "Display equations must be standalone `$$...$$` blocks" in prompt
    assert "\\begin{aligned}" in prompt
    assert "\\tag{" in prompt
    assert "Never use `\\(...\\)`" in prompt
    assert "Use Markdown tables for simple rectangular tables" in prompt
    assert "Use HTML tables for complex tables" in prompt
    assert "[illegible]" in prompt


def test_equation_normalization_skips_fenced_code():
    server = load_server()
    source = "Before \\(x+y\\).\n\\[a=b\\]\n```python\nprint('\\(keep\\)')\n```\nAfter"
    normalized = server._normalize_equations(source)
    assert "Before $x+y$." in normalized
    assert "$$a=b$$" in normalized
    assert "print('\\(keep\\)')" in normalized


def test_google_payload_uses_inline_data(monkeypatch):
    server = load_server()
    captured = {}

    class Response:
        status_code = 200
        text = "ok"

        def json(self):
            return {"candidates": [{"content": {"parts": [{"text": "# Done"}]}}]}

    class Client:
        def __init__(self, timeout):
            captured["timeout"] = timeout

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def post(self, url, headers=None, json=None):
            captured["url"] = url
            captured["headers"] = headers
            captured["json"] = json
            return Response()

    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    monkeypatch.setattr(server.httpx, "Client", Client)
    text = server._call_google(
        "prompt",
        [{"image_mime_type": "image/png", "image_base64": "AAA"}],
        "gemini-test",
        7.0,
    )
    assert text == "# Done"
    assert captured["url"].endswith("/models/gemini-test:generateContent")
    parts = captured["json"]["contents"][0]["parts"]
    assert parts[0] == {"text": "prompt"}
    assert parts[1]["inline_data"] == {"mime_type": "image/png", "data": "AAA"}


def test_ollama_payload_uses_images_and_stream_false(monkeypatch):
    server = load_server()
    captured = {}

    class Response:
        status_code = 200
        text = "ok"

        def json(self):
            return {"response": "# Local"}

    class Client:
        def __init__(self, timeout):
            captured["timeout"] = timeout

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def post(self, url, json=None):
            captured["url"] = url
            captured["json"] = json
            return Response()

    monkeypatch.setattr(server.httpx, "Client", Client)
    text = server._call_ollama("prompt", [{"image_base64": "AAA"}], "llava-test", 5.0)
    assert text == "# Local"
    assert captured["url"].endswith("/api/generate")
    assert captured["json"]["images"] == ["AAA"]
    assert captured["json"]["stream"] is False


def test_tool_integration_with_generated_pdf_and_mocked_provider(tmp_path, monkeypatch):
    server = load_server()
    pdf_path = make_pdf(tmp_path / "tiny.pdf")
    calls = []

    def fake_generate(provider, prompt, page_payloads, model, timeout):
        calls.append((provider, prompt, page_payloads, model, timeout))
        return "Title\n\n\\[E=mc^2\\]\n\n| A | B |\n| --- | --- |\n| 1 | 2 |"

    monkeypatch.setattr(server, "_generate", fake_generate)
    raw = server.convert_pdf_to_markdown(
        str(pdf_path),
        provider="ollama",
        model="vision-test",
        pages="1",
        render_dpi=72,
        timeout_seconds=3,
    )
    result = json.loads(raw)
    assert result["ok"] is True
    assert result["provider"] == "ollama"
    assert result["model"] == "vision-test"
    assert result["page_count"] == 1
    assert result["pages_converted"] == [1]
    assert "<!-- Page 1 -->" in result["markdown"]
    assert "$$E=mc^2$$" in result["markdown"]
    assert calls[0][2][0]["image_mime_type"] == "image/png"
    assert calls[0][2][0]["embedded_text"].strip()
