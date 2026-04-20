# OpenCode Runtime Sequence (Debug JSONL)

This reference captures a practical way to reconstruct OpenCode runtime behavior from a debug JSONL log.

## Hooks vs Events

OpenCode has two fundamentally different interception mechanisms. Knowing which is which prevents confusion when reading debug logs.

| Concept | Symbol | Where it appears | Can mutate? | Examples |
|---------|--------|------------------|-------------|----------|
| **Hooks** | 🔧 | Top-level `type` field | **Yes** — plugins receive `(input, output)` and can mutate `output` | `config`, `chat.message`, `experimental.chat.system.transform`, `chat.params`, `chat.headers`, `tool.definition`, `tool.execute.before`, `tool.execute.after`, `experimental.chat.messages.transform` |
| **Events** | 📡 | Nested inside `type: "event"` records | **No** — read-only state change notifications | `session.created`, `session.updated`, `session.status`, `session.diff`, `message.updated`, `message.part.updated`, `message.part.delta` |

**Important overlap**: Some names exist as **both** a hook and an event type:

- `tool.execute.before` — appears as a 🔧 hook (top-level `type`) **and** as a 📡 event (nested inside `type: "event"`)
- `tool.execute.after` — appears as a 🔧 hook (top-level `type`) **and** as a 📡 event (nested inside `type: "event"`)

> **Rule of thumb**: If it appears as a top-level `type`, it's a hook. If it appears inside `.payload[0].event.type`, it's an event.

## Authoritative Sources

- OpenCode docs: https://opencode.ai/docs/server
- OpenCode docs: https://opencode.ai/docs/sdk
- OpenCode docs: https://opencode.ai/docs/agents
- OpenCode docs: https://opencode.ai/docs/cli

## How to Tell Hooks from Events in Debug Logs

```bash
# Show only hooks (top-level types that are not "event")
jq 'select(.type != "event") | .type' opencode-debug.jsonl

# Show only events (nested inside event records)
jq 'select(.type=="event") | .payload[0].event.type' opencode-debug.jsonl

# Show both for the same name (e.g., tool.execute.before)
jq 'select(.type=="tool.execute.before" or (.type=="event" and .payload[0].event.type=="tool.execute.before")) | {type, timestamp}' opencode-debug.jsonl
```

## Minimal Extraction Commands

```bash
# Top-level record type counts (hooks + the event container)
jq -r '.type' opencode-debug.jsonl | sort | uniq -c

# Event subtype counts (read-only notifications)
jq -r 'select(.type=="event") | .payload[0].event.type' opencode-debug.jsonl | sort | uniq -c

# Session tree (parent -> child) — built from session.created events
jq -r 'select(.type=="event" and .payload[0].event.type=="session.created") |
  [.payload[0].event.properties.sessionID, (.payload[0].event.properties.info.parentID // "-"), .payload[0].event.properties.info.title] | @tsv' opencode-debug.jsonl

# Tool lifecycle hooks (execution boundaries)
jq -r 'select(.type=="tool.execute.before" or .type=="tool.execute.after") |
  [.timestamp, .type, .payload[0].tool] | @tsv' opencode-debug.jsonl
```

## Observed Pattern in the Current Log

From the attached `opencode-debug.jsonl`:

- 110 lines total.
- Top-level record types (hooks and event containers):
  - `event` (dominant — these are the event containers)
  - `chat.message` (🔧 hook)
  - `experimental.chat.system.transform` (🔧 hook)
  - `tool.execute.before` and `tool.execute.after` (🔧 hooks, also appear as 📡 events)
- Two sessions were created (📡 events):
  - parent session
  - child subagent session with `parentID` set to the parent
- Two tools executed in this run:
  - `task` (spawned subagent)
  - `bash` (inside child session)

## Canonical Runtime Timeline

1. 📡 Parent `session.created`
2. 🔧 User `chat.message`
3. 📡 Parent `session.status=busy`
4. 🔧 `experimental.chat.system.transform` (title/system prompt shaping)
5. 📡 Assistant message parts stream (`step-start`, `reasoning`, `tool`)
6. 🔧📡 `tool.execute.before:task`
7. 📡 Child `session.created` (linked by `parentID`)
8. 📡 Child prompt and child status busy
9. 🔧📡 Child `tool.execute.before:bash`
10. 📡 Child tool state transitions (`pending -> running -> completed`)
11. 🔧📡 `tool.execute.after:bash`
12. 📡 Child session reaches idle
13. 🔧📡 `tool.execute.after:task` in parent
14. 📡 Parent reaches idle

> **Key**: Hooks (🔧) are interception points you can act on. Events (📡) are historical state changes you observe. Where both symbols appear, the same name functions as both a hook and an event type.

## Tool Part State Lifecycle

`message.part.updated` events (📡, not hooks) with `part.type == "tool"` map runtime state transitions:

1. `pending`
2. `running` (can appear multiple times as metadata/output updates stream)
3. terminal state:
   - `completed` with output/metadata, or
   - `error` with error payload

This is an **event-only** stream — you observe these transitions; you cannot mutate them. If you need to intercept tool execution, use the `tool.execute.before` and `tool.execute.after` **hooks** instead.

## Reading Heuristics

- **Hooks (🔧)** are where you inject behavior — they appear as top-level `type` values and can be mutated by plugins.
- **Events (📡)** are where you observe history — they are nested inside `type: "event"` records and are read-only.
- Use `session.created` (📡 event) + `parentID` to rebuild orchestration.
- Use `tool.execute.before/after` (🔧 hooks, also 📡 events) for exact execution boundaries.
- Use `message.part.updated` (📡 event) for user-visible streaming states.
- Use `experimental.chat.system.transform` (🔧 hook) entries to understand injected prompts and role changes.
- When you see the same name at top-level and inside an event payload, remember: the top-level one is the hook (interception point), the nested one is the event (notification).

## Common Mistakes While Debugging

- **Confusing hooks with events**: Trying to mutate something that is only an event (e.g., `session.created`, `message.part.updated`) will not work. Only hooks support mutation via `(input, output)`.
- **Looking for `session.created` as a hook**: It is **only** an event. You cannot intercept session creation; you can only observe it after the fact.
- **Not realizing `tool.execute.before` fires as both**: It appears as a 🔧 top-level hook (where you can modify behavior) **and** as a 📡 nested event (where you can only observe that it happened).
- Looking only at `tool.execute.after` and missing failed calls that never complete.
- Ignoring `message.part.updated` events where the same call ID changes state over time.
- Treating `session.updated` as execution boundaries (they are state snapshots, not hard boundaries).
