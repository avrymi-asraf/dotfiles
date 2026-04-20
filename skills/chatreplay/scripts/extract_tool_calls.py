#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""
Extract every tool call and its outcome from a .chatreplay.json file.

Usage:
        uv run skills/chatreplay/scripts/extract_tool_calls.py <file.chatreplay.json>
        uv run skills/chatreplay/scripts/extract_tool_calls.py <file.chatreplay.json> --json
        uv run skills/chatreplay/scripts/extract_tool_calls.py <file.chatreplay.json> --errors
"""

import argparse
import json
import sys
import re
from pathlib import Path


def get_text_from_content(content: list) -> str:
    parts = []
    for part in content:
        if part.get("type") == 1:
            t = part.get("text", "").strip()
            if t:
                parts.append(t)
    return "\n".join(parts)


def get_thinking_text(content: list) -> str:
    for part in content:
        if part.get("type") == 2:
            val = part.get("value", {})
            if isinstance(val, dict) and val.get("type") == "thinking":
                thinking = val.get("thinking", {})
                if isinstance(thinking, dict):
                    text = thinking.get("text", "")
                    if text and not thinking.get("encrypted", False):
                        return text
    return ""


def get_explicit_tool_calls(content: list) -> list:
    """Extract any explicit tool_call parts from the content."""
    calls = []
    for part in content:
        if part.get("type") == 2:
            val = part.get("value", {})
            if isinstance(val, dict) and val.get("type") == "tool_call":
                tc = val.get("toolCall", {})
                calls.append({
                    "id":    tc.get("id", ""),
                    "name":  tc.get("name", "?"),
                    "input": tc.get("input", {}),
                })
    return calls


def classify_tool_result(result_text: str) -> dict:
    """
    Infer tool name and success/failure from the tool result text.
    Returns {"tool": name, "status": "ok"|"error", "error_detail": str}
    """
    rt = result_text.strip()
    rt_lower = rt.lower()

    # Detect errors
    if rt_lower.startswith("error:") or "must have required property" in rt_lower:
        m = re.search(r"required property '(\w+)'", rt)
        missing = m.group(1) if m else "unknown"
        return {"status": "error", "error_detail": f"Missing required property: '{missing}'"}

    # Classify by content patterns
    if "successfully wrote todo list" in rt_lower:
        return {"tool": "manage_todo_list", "status": "ok"}
    if "the following files were successfully edited" in rt_lower:
        files = [l.strip() for l in rt.splitlines() if l.strip() and not l.strip().startswith("The")]
        return {"tool": "apply_patch", "status": "ok", "files_edited": files}
    if "total results" in rt_lower:
        return {"tool": "grep_search / file_search", "status": "ok"}
    if rt_lower.strip() == "ok":
        return {"tool": "run_in_terminal", "status": "ok"}
    if "---\nname:" in rt or "## " in rt and "lambda" in rt_lower:
        return {"tool": "read_file(SKILL.md)", "status": "ok"}
    if "module.exports" in rt or rt.startswith("{") or rt.startswith("//"):
        # Distinguish V1 (JS) vs V2 (JSON) configs
        if rt.strip().startswith("{"):
            return {"tool": "read_file(.json)", "status": "ok"}
        return {"tool": "read_file(.js)", "status": "ok"}

    return {"tool": "unknown", "status": "ok"}


def extract_calls(path: str, output_json: bool = False, errors_only: bool = False):
    with open(path) as f:
        data = json.load(f)

    logs   = data.get("logs", [])
    prompt = data.get("prompt", "?")

    # Use the last log for the full message history
    if not logs:
        print("No logs found.", file=sys.stderr)
        return

    last_log = logs[-1]
    messages = last_log["requestMessages"]["messages"]

    calls = []
    turn  = 0

    for i in range(len(messages)):
        msg = messages[i]
        if msg.get("role") != 2:
            continue  # only process assistant messages

        content      = msg.get("content", [])
        spoken_text  = get_text_from_content(content).strip()
        thinking     = get_thinking_text(content)

        # Check if the next message is a tool result
        if i + 1 >= len(messages) or messages[i + 1].get("role") != 3:
            continue

        turn += 1
        tool_result_content = messages[i + 1].get("content", [])
        tool_result_text    = get_text_from_content(tool_result_content)

        # Find which log this message belongs to (for token counts)
        # The turn number in the log array corresponds to which log added these messages
        log_index     = min(turn - 1, len(logs) - 1)
        log_meta      = logs[log_index].get("metadata", {})
        usage         = log_meta.get("usage", {})
        completion_tokens = usage.get("completion_tokens", 0)
        reasoning_tokens  = usage.get("completion_tokens_details", {}).get("reasoning_tokens", 0)

        # Try to get explicit tool name first
        explicit_calls = get_explicit_tool_calls(content)

        # Classify from result
        classification = classify_tool_result(tool_result_text)

        # Build the record
        if explicit_calls:
            for ec in explicit_calls:
                record = {
                    "turn":        turn,
                    "tool":        ec["name"],
                    "input":       ec["input"],
                    "result":      tool_result_text[:300],
                    "status":      classification.get("status", "ok"),
                    "error":       classification.get("error_detail", ""),
                    "spoken":      spoken_text[:120],
                    "thinking_excerpt": thinking.split("\n")[0][:150] if thinking else "",
                    "completion_tokens": completion_tokens,
                    "reasoning_tokens":  reasoning_tokens,
                }
                calls.append(record)
        else:
            # Infer tool name from classification + thinking
            tool_name = classification.get("tool", "?")
            if not tool_name or tool_name == "unknown":
                # Try to find a tool name in thinking
                m = re.search(
                    r"\b(read_file|apply_patch|grep_search|file_search|run_in_terminal|"
                    r"manage_todo_list|list_dir|semantic_search|fetch_webpage|"
                    r"mcp_cdn_\w+|runSubagent)\b",
                    thinking,
                )
                if m:
                    tool_name = m.group(1)

            record = {
                "turn":        turn,
                "tool":        tool_name,
                "input":       {},
                "result":      tool_result_text[:300],
                "status":      classification.get("status", "ok"),
                "error":       classification.get("error_detail", ""),
                "spoken":      spoken_text[:120],
                "thinking_excerpt": thinking.split("\n")[0][:150] if thinking else "",
                "completion_tokens": completion_tokens,
                "reasoning_tokens":  reasoning_tokens,
                "files_edited": classification.get("files_edited", []),
            }
            calls.append(record)

    # Filter
    if errors_only:
        calls = [c for c in calls if c["status"] == "error"]

    if output_json:
        # Machine-readable output goes to stdout
        print(json.dumps(calls, indent=2))
        return

    # Pretty-print table
    # Human-oriented output goes to stderr so JSON/pipe consumers can use stdout
    print("=" * 80, file=sys.stderr)
    print(f"TOOL CALL ANALYSIS: {Path(path).name}", file=sys.stderr)
    print(f"User request: {prompt}", file=sys.stderr)
    print(f"Total tool calls: {len(calls)}", file=sys.stderr)
    errors = sum(1 for c in calls if c["status"] == "error")
    print(f"Errors/retries: {errors}", file=sys.stderr)
    print("=" * 80, file=sys.stderr)

    for rec in calls:
        status_icon = "✅" if rec["status"] == "ok" else "❌"
        print(f"\n{status_icon} Turn {rec['turn']:2d}:  {rec['tool']}", file=sys.stderr)

        if rec["spoken"]:
            print(f"   💬 Narration: \"{rec['spoken']}\"", file=sys.stderr)

        if rec["thinking_excerpt"]:
            print(f"   🧠 Thinking:  {rec['thinking_excerpt']}", file=sys.stderr)

        if rec["input"] and isinstance(rec["input"], dict):
            for k, v in list(rec["input"].items())[:3]:
                vs = str(v)[:120]
                print(f"   📥 Input.{k}: {vs}", file=sys.stderr)

        # Show result
        result_preview = rec["result"].replace("\n", " | ")[:200]
        if rec["status"] == "error":
            print(f"   ❌ ERROR: {rec['error']}", file=sys.stderr)
            print(f"   Raw: {result_preview}", file=sys.stderr)
        else:
            print(f"   📤 Result: {result_preview}", file=sys.stderr)

        if rec.get("files_edited"):
            for fp in rec["files_edited"]:
                print(f"   📝 Edited: {fp}", file=sys.stderr)

        if rec["completion_tokens"]:
            print(f"   🔢 Tokens: {rec['completion_tokens']} completion ({rec['reasoning_tokens']} reasoning)", file=sys.stderr)

    print("\n" + "=" * 80, file=sys.stderr)
    print("SUMMARY", file=sys.stderr)
    print("-" * 80, file=sys.stderr)
    tool_counts: dict = {}
    for rec in calls:
        tool_counts[rec["tool"]] = tool_counts.get(rec["tool"], 0) + 1
    for tool, count in sorted(tool_counts.items(), key=lambda x: -x[1]):
        print(f"  {tool}: {count} call(s)", file=sys.stderr)

    if errors:
        print(f"\n⚠️  {errors} tool call(s) failed and were retried.", file=sys.stderr)
        failed_tools = [c["tool"] for c in calls if c["status"] == "error"]
        for ft in set(failed_tools):
            print(f"  - {ft}: check required parameters in SKILL.md tool list", file=sys.stderr)

    print("=" * 80, file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <file.chatreplay.json> [--json] [--errors]")
        sys.exit(1)

    fpath       = sys.argv[1]
    out_json    = "--json" in sys.argv
    errors_only = "--errors" in sys.argv

    extract_calls(fpath, output_json=out_json, errors_only=errors_only)