#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""
Full structured dump of a .chatreplay.json file.

Usage:
    uv run skills/chatreplay/scripts/parse_chatreplay.py <file.chatreplay.json>
"""

import argparse
import json
import sys
from pathlib import Path


ROLE_NAMES = {0: "SYSTEM", 1: "USER/CONTEXT", 2: "ASSISTANT", 3: "TOOL_RESULT"}
PART_TYPE_NAMES = {1: "text", 2: "structured", 3: "cache_control"}

CYAN  = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED   = "\033[91m"
BLUE  = "\033[94m"
DIM   = "\033[2m"
RESET = "\033[0m"
BOLD  = "\033[1m"


def role_color(role: int) -> str:
    return {0: DIM, 1: BLUE, 2: GREEN, 3: YELLOW}.get(role, RESET)


def print_section(title: str, width: int = 80):
    print(f"\n{BOLD}{'=' * width}{RESET}")
    print(f"{BOLD}  {title}{RESET}")
    print(f"{BOLD}{'=' * width}{RESET}")


def print_part(part: dict, indent: int = 4):
    pad = " " * indent
    ptype = part.get("type")
    type_label = PART_TYPE_NAMES.get(ptype, f"type-{ptype}")

    if ptype == 1:  # text
        text = part.get("text", "")
        if text.strip():
            print(f"{pad}[{type_label}]")
            for line in text.split("\n"):
                print(f"{pad}  {line}")
        else:
            print(f"{pad}[{type_label}] (empty)")

    elif ptype == 2:  # structured
        val = part.get("value", {})
        if not isinstance(val, dict):
            print(f"{pad}[{type_label}] value={repr(val)[:100]}")
            return

        vtype = val.get("type", "?")

        if vtype == "stateful_marker":
            inner = val.get("value", {})
            model_id = inner.get("modelId", "?") if isinstance(inner, dict) else "?"
            marker = inner.get("marker", "") if isinstance(inner, dict) else ""
            print(f"{pad}[{type_label} / stateful_marker] model={model_id} marker={marker[:40]}…")

        elif vtype == "thinking":
            thinking = val.get("thinking", {})
            if isinstance(thinking, dict):
                is_enc = thinking.get("encrypted", False)
                tokens = thinking.get("tokens", "?")
                text = thinking.get("text", "")
                if is_enc or not text:
                    print(f"{pad}[{type_label} / thinking] (encrypted) tokens={tokens}")
                else:
                    print(f"{pad}[{type_label} / thinking] tokens={tokens}")
                    for line in text.split("\n"):
                        print(f"{pad}  {DIM}{line}{RESET}")

        elif vtype == "tool_call":
            tc = val.get("toolCall", {})
            name = tc.get("name", "?")
            tc_id = tc.get("id", "?")
            inp = tc.get("input", {})
            print(f"{pad}[{type_label} / {CYAN}TOOL_CALL{RESET}] {CYAN}{name}{RESET} (id={tc_id})")
            if isinstance(inp, dict):
                for k, v in inp.items():
                    vs = str(v)
                    if len(vs) > 200:
                        print(f"{pad}  {k}: {vs[:200]}…")
                    else:
                        print(f"{pad}  {k}: {vs}")
            else:
                print(f"{pad}  input: {str(inp)[:200]}")

        else:
            print(f"{pad}[{type_label} / {vtype}] {repr(str(val))[:100]}")

    elif ptype == 3:  # cache_control
        ct = part.get("cacheType", "?")
        print(f"{pad}[cache_control] type={ct}")

    else:
        print(f"{pad}[unknown-type-{ptype}] {repr(part)[:100]}")


def print_message(msg: dict, index: int):
    role_num = msg.get("role")
    role_name = ROLE_NAMES.get(role_num, f"role-{role_num}")
    color = role_color(role_num)
    content = msg.get("content", [])
    print(f"\n  {color}▶ msg[{index}] {role_name}{RESET}  ({len(content)} parts)")
    for part in content:
        print_part(part)


def print_metadata(meta: dict):
    print(f"  Model:           {meta.get('model', '?')}")
    print(f"  Duration:        {meta.get('duration', '?')} ms")
    print(f"  Time-to-first:   {meta.get('timeToFirstToken', '?')} ms")
    usage = meta.get("usage", {})
    pt = usage.get("prompt_tokens", "?")
    ct = usage.get("completion_tokens", "?")
    rt = usage.get("completion_tokens_details", {}).get("reasoning_tokens", 0)
    cached = usage.get("prompt_tokens_details", {}).get("cached_tokens", 0)
    print(f"  Tokens:          prompt={pt} (cached={cached})  completion={ct} (reasoning={rt})")
    tools = meta.get("tools", [])
    print(f"  Tools available: {len(tools)}")


def parse_file(path: str):
    with open(path) as f:
        data = json.load(f)

    print_section(f"CHATREPLAY: {Path(path).name}")
    print(f"  Prompt:    {data.get('prompt', '?')}")
    print(f"  PromptID:  {data.get('promptId', '?')}")
    print(f"  Log count: {data.get('logCount', '?')}")

    logs = data.get("logs", [])
    prev_msg_count = 0

    for i, log in enumerate(logs):
        log_id   = log.get("id", "?")
        log_type = log.get("type", "?")
        log_name = log.get("name", "?")
        meta     = log.get("metadata", {})
        req      = log.get("requestMessages", {})
        resp     = log.get("response", {})
        messages = req.get("messages", [])
        resp_msgs = resp.get("message", [])
        resp_type = resp.get("type", "?")

        print_section(f"LOG {i} / {log_id}  ({log_type} — {log_name})", width=70)
        print_metadata(meta)

        # Show only new messages (delta since previous log)
        new_msgs = messages[prev_msg_count:]
        if new_msgs:
            print(f"\n  {BOLD}--- New messages in this turn ({len(new_msgs)}) ---{RESET}")
            for j, msg in enumerate(new_msgs):
                print_message(msg, prev_msg_count + j)
        else:
            print(f"\n  (first turn — {len(messages)} messages in context)")
            for j, msg in enumerate(messages):
                print_message(msg, j)

        prev_msg_count = len(messages)

        # Response
        print(f"\n  {BOLD}--- Response ({resp_type}) ---{RESET}")
        for part in resp_msgs:
            if isinstance(part, str):
                print(f"    {GREEN}{part[:500]}{RESET}")
            elif isinstance(part, dict):
                print_part(part, indent=4)

    print_section("SESSION COMPLETE", width=70)
    print(f"  Total LLM calls:    {len(logs)}")
    total_tokens = sum(
        log.get("metadata", {}).get("usage", {}).get("total_tokens", 0)
        for log in logs
    )
    total_ms = sum(
        log.get("metadata", {}).get("duration", 0)
        for log in logs
    )
    print(f"  Total tokens used:  {total_tokens}")
    print(f"  Total time:         {total_ms} ms  ({total_ms/1000:.1f}s)")
    if logs:
        final_resp = logs[-1].get("response", {}).get("message", [])
        if final_resp:
            print(f"\n  {BOLD}FINAL ANSWER:{RESET}")
            ans = final_resp[0] if isinstance(final_resp[0], str) else str(final_resp[0])
            print(f"  {ans[:1000]}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Full structured dump of a .chatreplay.json file")
    parser.add_argument("file", help="Path to .chatreplay.json file")
    parser.add_argument("-p", "--profile", help="AWS profile (unused but available)")
    args = parser.parse_args(argv)
    try:
        parse_file(args.file)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()