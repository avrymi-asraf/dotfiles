---
name: chatreplay
description: Parse and interpret `.chatreplay.json` files — a log format that captures the full agentic session between a user, an AI assistant (GitHub Copilot / VS Code agent), and its tools. Use this skill when asked to read, analyze, summarize, or debug a chatreplay file.
---

# Chatreplay Protocol Reference

A `.chatreplay.json` file is a complete replay log of an agentic AI session. It contains every LLM request-response cycle, the full message history (including system prompt, user context, assistant reasoning, and tool results), and rich metadata about timing and token usage.

## Top-Level Structure

```json
{
  "prompt":    "the original user request (human-readable label)",
  "promptId":  "UUID-style string, e.g. '5afe6a1a-prompt'",
  "logCount":  13,
  "logs":      [ /* array of Log entries */ ]
}
```

| Field | Type | Meaning |
|-------|------|---------|
| `prompt` | string | The plain-English task the user submitted |
| `promptId` | string | Identifier for this replay session |
| `logCount` | integer | Number of LLM API calls recorded; equals `logs.length` |
| `logs` | array | One entry per LLM call (one "turn" of the agentic loop) |

---

## Log Entry

Each element in `logs` represents **one LLM API round-trip**. The `requestMessages` field is the full context sent to the model, and `response` is what the model returned.

```json
{
  "id":              "5afe6a1a",         // short hex ID unique to this turn
  "kind":            "request",          // always "request" in current version
  "type":            "ChatMLSuccess",    // success/failure status
  "name":            "panel/editAgent",  // which VS Code panel triggered this
  "metadata":        { ... },            // timing, model, token counts, tool list
  "requestMessages": { "messages": [...] },
  "response":        { "type": "success", "message": [...] }
}
```

### Growing History Pattern

The `requestMessages.messages` array **grows by 2 with every turn**:
each turn appends one assistant message and one tool_result message.
Turn N always contains the complete conversation history up to that point.
To find what happened in turn N, look at the last 2 messages in `requestMessages.messages`.

---

## Metadata

```json
{
  "model":             "gpt-5-mini",
  "maxPromptTokens":   127997,
  "maxResponseTokens": 64000,
  "location":          7,              // internal VS Code panel slot
  "reasoning": {
    "effort":  "high",
    "summary": "detailed"
  },
  "startTime":        "2026-04-06T10:06:58.277Z",
  "endTime":          "2026-04-06T10:07:26.363Z",
  "duration":         28086,           // milliseconds
  "ourRequestId":     "UUID",
  "requestId":        "UUID",
  "serverRequestId":  "UUID",
  "timeToFirstToken": 10091,           // ms until first streaming token
  "usage": {
    "prompt_tokens":              27023,
    "completion_tokens":           1821,
    "total_tokens":               28844,
    "prompt_tokens_details": {
      "cached_tokens": 0
    },
    "completion_tokens_details": {
      "reasoning_tokens":          1728,   // tokens used for chain-of-thought
      "accepted_prediction_tokens":   0,
      "rejected_prediction_tokens":   0
    }
  },
  "tools": [ /* array of tool definitions (name, description, parameters) */ ]
}
```

**Important metadata signals:**
- `reasoning_tokens` — how much the model "thought" before answering; high values indicate complex reasoning.
- `timeToFirstToken` — latency before streaming started.
- `cached_tokens` — how much prompt was served from KV cache (0 means no caching benefit).
- `tools` — the full JSON schema of every tool available to the agent in this session.

---

## Message Structure

Each message in `requestMessages.messages` has:
```json
{ "role": <integer>, "content": [ <parts> ] }
```

### Role Encoding (integer)

| Integer | Semantic Role | Meaning |
|---------|---------------|---------|
| `0` | system | System prompt (agent instructions, persona, policies) |
| `1` | user/context | User message, environment info, workspace context |
| `2` | assistant | Model output (text, tool calls, thinking) |
| `3` | tool_result | Tool execution output returned to the model |

### Content Part Types (integer)

Each item in `content` is `{ "type": <integer>, ... }`:

| Integer | Name | Fields | Meaning |
|---------|------|--------|---------|
| `1` | text | `text: string` | Plain text content |
| `2` | structured | `value: object` | Tool call, thinking, or opaque state marker |
| `3` | cache_control | `cacheType: string` | Marks content for prompt caching (e.g. `"ephemeral"`) |

---

## Type-2 Structured Parts

The `value` field of a type-2 part has a `type` discriminator:

### `stateful_marker`
```json
{
  "type": "stateful_marker",
  "value": {
    "modelId": "gpt-5-mini",
    "marker":  "<base64-encrypted opaque state>"
  }
}
```
An opaque token that encodes the model's internal state for the next continuation.
**The actual tool call details are encrypted inside this marker** and cannot be read directly.
To know what tool was called, cross-reference with the **thinking text** and the **following tool_result message**.

### `thinking`
```json
{
  "type": "thinking",
  "thinking": {
    "id":        "<base64 identifier>",
    "text":      "The model's chain-of-thought reasoning (may be plain text or empty if encrypted)",
    "encrypted": false,
    "tokens":    1728
  }
}
```
The model's internal chain-of-thought. When `encrypted: false`, the `text` field contains readable reasoning that describes what the model was planning to do, which tool it was about to call, and why.

### `tool_call` (when visible)
```json
{
  "type": "tool_call",
  "toolCall": {
    "id":    "call_abc123",
    "name":  "apply_patch",
    "input": { "explanation": "...", "input": "*** Begin Patch\n..." }
  }
}
```
Explicit tool call. Only appears when not fully encoded in the stateful_marker.

---

## Response Object

```json
{
  "type":    "success",
  "message": [ "plain text string" ]
}
```
The `message` array contains the assistant's response for that turn. In most turns it is a single string. The **final log's response** contains the agent's concluding answer to the user.

---

## Reading a Chatreplay File: Step-by-Step

### 1. Get the high-level picture
```
prompt       → what the user asked
logCount     → how many LLM calls were made (complexity indicator)
logs[*].metadata.duration  → how long each turn took
logs[*].metadata.usage     → token cost per turn
```

### 2. Reconstruct the agentic loop
For turn N (0-indexed):
- **What the model decided**: `logs[N].response.message[0]` — the assistant's spoken response
- **What tool was called**: infer from the thinking text in `logs[N+1].requestMessages.messages[-2]` (the assistant message appended in the next log), or from `logs[N+1].requestMessages.messages[-1]` (the tool result)
- **Tool output**: `logs[N+1].requestMessages.messages[-1].content[0].text`

### 3. Extract the full conversation
Use the **last log** (`logs[logCount-1]`). Its `requestMessages.messages` contains the entire conversation history. Walk it in order:
- role 0 → system prompt
- role 1 → user/context messages
- role 2 → assistant turns (look for `text` parts and `thinking` parts)
- role 3 → tool results (look for `text` parts)

### 4. Identify errors and retries
Look for tool_result messages (role=3) containing `ERROR:`. Each error is followed by another assistant message that retries the tool with corrected input.

### 5. Find the final answer
`logs[logCount-1].response.message[0]` — the agent's final response to the user.

---

## Annotated Example Walk-through

Given a file with 13 logs, here is how the session unfolds:

```
Log  0: User asks "add issuer X to CDN_DEV:kss"
         → Model reads SKILL.md guidance (tool call inferred from thinking)
         → response: "I'll read the lambda-edge SKILL.md..."

Log  1: Tool result: SKILL.md content
         → Model creates a TODO list
         → response: "Creating a TODO list for the kss issuer update first."

Log  2: Tool result: "Successfully wrote todo list"
         → Model searches for kss config files
         → response: (empty — silent tool call)

Log  3: Tool result: 3 file paths found
         → Model reads V1 config file
         → response: (empty)

Log  4: Tool result: V1 cfg.js content
         → Model reads V2 config file
         → response: (empty)

Log  5: Tool result: V2 config.json content
         → Model attempts apply_patch (missing 'explanation' field)
         → response: "I'll patch the V1 and V2 config files..."

Log  6: Tool result: ERROR (missing required property 'explanation')
         → Model retries apply_patch with correct input
         → response: (empty)

Log  7: Tool result: V1 file edited successfully
         → Model patches V2 config
         → response: (empty)

Log  8: Tool result: V2 file edited successfully
         → Model updates TODO list statuses
         → response: "Updating TODO statuses..."

Log  9: Tool result: "Successfully wrote todo list"
         → Model runs validation command (missing 'isBackground' field)
         → response: (empty)

Log 10: Tool result: ERROR (missing required property 'isBackground')
         → Model retries run_in_terminal with correct input
         → response: (empty)

Log 11: Tool result: "OK" (validation passed)
         → Model marks all todos done
         → response: (empty)

Log 12: Tool result: "Successfully wrote todo list"
         → FINAL RESPONSE: Summary of changes made
```

---

## Common Tool Names in These Logs

| Tool | Purpose |
|------|---------|
| `read_file` | Read file contents by path and line range |
| `apply_patch` | Edit files via V4A diff format (requires `explanation` + `input`) |
| `grep_search` | Fast text/regex search across workspace files |
| `file_search` | Find files by glob pattern |
| `semantic_search` | Natural language search across codebase |
| `run_in_terminal` | Execute shell commands (requires `command`, `explanation`, `goal`, `isBackground`) |
| `manage_todo_list` | Create/update a structured task list |
| `list_dir` | List directory contents |
| `fetch_webpage` | Fetch and summarize a URL |
| `get_errors` | Get compile/lint errors from files |
| `mcp_cdn_get_distribution_data` | Get CloudFront distribution config + Lambda code |
| `mcp_cdn_get_cdn_logs_by_time` | Query CDN logs from Athena |
| `mcp_cdn_get_account_rem_profile` | Map AWS account IDs ↔ REM profile names |

---

## Scripts

Three helper scripts are in the `scripts/` directory:

| Script | Usage |
|--------|-------|
| `parse_chatreplay.py` | Full structured dump — all turns, roles, types, values |
| `summarize_session.py` | Human-readable narrative summary of the session |
| `extract_tool_calls.py` | Inferred list of every tool call and its outcome |

Run any script with:
```bash
python3 scripts/<script>.py path/to/file.chatreplay.json
```

---

## Quick Reference Card

```
File:       { prompt, promptId, logCount, logs[] }
Log:        { id, kind, type, name, metadata, requestMessages, response }
Metadata:   { model, duration, usage{tokens, reasoning_tokens}, tools[] }
Messages:   role 0=system  1=user  2=assistant  3=tool_result
Parts:      type 1=text  type 2=structured  type 3=cache_control
Type-2:     stateful_marker (opaque)  |  thinking (reasoning)  |  tool_call
Response:   { type:"success", message:["text"] }

Loop:       Each turn appends +2 msgs: assistant message + tool_result
Errors:     role-3 parts containing "ERROR:" → retry in next turn
Final:      logs[last].response.message[0] = agent's answer to user
```