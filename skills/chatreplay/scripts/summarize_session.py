#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""
Human-readable narrative summary of a .chatreplay.json session.

Usage:
        uv run skills/chatreplay/scripts/summarize_session.py <file.chatreplay.json>
"""

import argparse
import json
import sys
from pathlib import Path


def get_thinking_text(content: list) -> str:
    """Extract readable thinking text from an assistant message's content parts."""
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


def get_text(content: list) -> str:
    """Extract all text parts from a message's content."""
    parts = []
    for part in content:
        if part.get("type") == 1:
            t = part.get("text", "").strip()
            if t:
                parts.append(t)
    return "\n".join(parts)


def infer_tool_called(thinking_text: str, tool_result: str) -> str:
    """
    Infer which tool was called based on thinking text and what the tool returned.
    Returns a short label like "read_file(path)" or "apply_patch(file)".
    """
    # Patterns based on tool result content
    result_lower = tool_result.lower()
    think_lower = thinking_text.lower()

    if "successfully wrote todo list" in result_lower:
        return "manage_todo_list(…)"
    if "successfully edited" in result_lower or "the following files were successfully edited" in result_lower:
        # Try to extract file name from result
        lines = tool_result.strip().splitlines()
        for line in lines:
            line = line.strip()
            if line and not line.startswith("The"):
                return f"apply_patch({line})"
        return "apply_patch(…)"
    if "total results" in result_lower or result_lower.startswith("/"):
        return "file_search / grep_search(…)"
    if "module.exports" in tool_result or tool_result.strip().startswith("{") or "---\nname:" in tool_result:
        # read_file result
        if "skill" in think_lower or "skill.md" in think_lower:
            return "read_file(SKILL.md)"
        # Try to detect file path from thinking
        import re
        m = re.search(r"read(?:ing)?\s+[`'\"]?([^\s'\"`,]+\.(?:js|json|md|tf|py))[`'\"]?", think_lower)
        if m:
            return f"read_file({m.group(1)})"
        return "read_file(…)"
    if result_lower.strip() == "ok":
        return "run_in_terminal(validation)"
    if "error" in result_lower[:30]:
        # A failed call; look at what was missing
        import re
        m = re.search(r"required property '(\w+)'", tool_result)
        if m:
            return f"(FAILED — missing '{m.group(1)}')"
        return "(FAILED call)"
    if "name: lambda-edge" in tool_result or "## " in tool_result:
        return "read_file(SKILL.md)"
    return "tool_call(…)"


def summarize(path: str):
    with open(path) as f:
        data = json.load(f)

    prompt  = data.get("prompt", "?")
    logs    = data.get("logs", [])
    n_logs  = len(logs)

    print("=" * 70)
    print("CHATREPLAY SESSION SUMMARY")
    print("=" * 70)
    print(f"File:     {Path(path).name}")
    print(f"Request:  {prompt}")
    print(f"Turns:    {n_logs} LLM calls")

    # Collect stats
    total_ms     = 0
    total_tokens = 0
    total_reason = 0
    model_name   = ""

    for log in logs:
        m = log.get("metadata", {})
        total_ms     += m.get("duration", 0)
        u = m.get("usage", {})
        total_tokens += u.get("total_tokens", 0)
        total_reason += u.get("completion_tokens_details", {}).get("reasoning_tokens", 0)
        if not model_name:
            model_name = m.get("model", "?")

    print(f"Model:    {model_name}")
    print(f"Time:     {total_ms/1000:.1f}s total")
    print(f"Tokens:   {total_tokens:,} total  (reasoning: {total_reason:,})")
    print()

    # Step-by-step narrative
    print("STEP-BY-STEP NARRATIVE")
    print("-" * 70)

    # Use the last log to get the full message history
    last_log = logs[-1]
    messages = last_log["requestMessages"]["messages"]

    step = 0
    i = 0
    while i < len(messages):
        msg = messages[i]
        role = msg.get("role")

        # Skip system and user/context messages (they're setup, not steps)
        if role in (0, 1):
            i += 1
            continue

        if role == 2:  # assistant turn
            content = msg.get("content", [])
            spoken  = get_text(content).strip()
            thinking = get_thinking_text(content)

            # The following message (role 3) is the tool result
            if i + 1 < len(messages) and messages[i + 1].get("role") == 3:
                tool_result_content = messages[i + 1].get("content", [])
                tool_result_text    = get_text(tool_result_content)

                tool_label = infer_tool_called(thinking, tool_result_text)
                step += 1

                is_error  = "ERROR:" in tool_result_text[:50]
                is_retry  = "FAILED" in tool_label

                print(f"Step {step:2d}: {tool_label}")
                if spoken:
                    print(f"         💬 \"{spoken[:120]}\"")

                # Summarize the tool result
                result_summary = tool_result_text.strip()
                if len(result_summary) > 200:
                    result_summary = result_summary[:200] + "…"
                result_summary = result_summary.replace("\n", " | ")

                if is_error:
                    print(f"         ❌ RESULT: {result_summary}")
                else:
                    print(f"         ✅ RESULT: {result_summary}")

                if thinking:
                    # Show a 1-sentence summary of thinking
                    first_line = thinking.split("\n")[0].strip()
                    if first_line and len(first_line) > 10:
                        print(f"         🧠 Reasoning: {first_line[:150]}")

                print()
                i += 2  # skip the tool result message
            else:
                # No following tool result — this is the final assistant message
                i += 1

        elif role == 3:
            # Orphaned tool result (shouldn't happen normally)
            i += 1
        else:
            i += 1

    # Final answer
    final_resp = logs[-1].get("response", {}).get("message", [])
    if final_resp:
        final_text = final_resp[0] if isinstance(final_resp[0], str) else str(final_resp[0])
        print("-" * 70)
        print("FINAL ANSWER:")
        print()
        # Print with line wrapping
        for line in final_text.split("\n"):
            print(f"  {line}")
        print()

    print("=" * 70)
    print(f"Session complete: {step} tool calls in {n_logs} LLM turns, {total_ms/1000:.1f}s, {total_tokens:,} tokens")
    print("=" * 70)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Human-readable narrative summary of a .chatreplay.json session")
    parser.add_argument("file", help="Path to .chatreplay.json file")
    parser.add_argument("-p", "--profile", help="AWS profile (unused)")
    args = parser.parse_args(argv)
    try:
        summarize(args.file)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()