# OpenCode Hook Reference

This file is a practical reference for implementing plugin hooks that modify runtime behavior.

## Authoritative Sources

- OpenCode docs: https://opencode.ai/docs/plugins
- OpenCode docs: https://opencode.ai/docs/config
- OpenCode docs: https://opencode.ai/docs/tools
- OpenCode docs: https://opencode.ai/docs/agents
- OpenCode docs: https://opencode.ai/docs/server
- Hook type definitions (source): https://github.com/anomalyco/opencode/blob/main/packages/plugin/src/index.ts
- Plugin trigger implementation (source): https://github.com/anomalyco/opencode/blob/main/packages/opencode/src/plugin/index.ts
- Tool hook invocation path (source): https://github.com/anomalyco/opencode/blob/main/packages/opencode/src/session/prompt.ts

## Plugin Entry Contract

```ts
import type { Plugin } from "@opencode-ai/plugin"

export const MyPlugin: Plugin = async ({ project, client, $, directory, worktree }) => {
  return {
    // hooks map
  }
}
```

Hook functions generally use this shape:

```ts
"hook.name": async (input, output) => {
  // read input
  // mutate output
}
```

## Hook Types (Taxonomy)

Use this to decide quickly what kind of hook to write.

1. **Interception hooks**
  - Intercept a runtime step before or after execution.
  - Examples: `tool.execute.before`, `tool.execute.after`, `command.execute.before`, `shell.env`.
2. **Prompt and request shaping hooks**
  - Change what is sent to the model or provider.
  - Examples: `chat.message`, `chat.params`, `chat.headers`, `tool.definition`.
3. **Policy hooks**
  - Influence permission outcomes.
  - Example: `permission.ask`.
4. **Continuation and compaction hooks**
  - Control long-context continuation behavior.
  - Examples: `experimental.session.compacting`, `experimental.compaction.autocontinue`, `experimental.text.complete`.
5. **Observation hooks**
  - Listen to emitted runtime events without direct mutation of tool args/results.
  - Example: `event`.

## Hook Selection Cheat Sheet

| Need | Preferred Hook | Notes |
|------|----------------|-------|
| Validate or block tool inputs | `tool.execute.before` | Throw error to hard-stop |
| Normalize tool output | `tool.execute.after` | Good for redaction and metadata |
| Inject env vars to shell runs | `shell.env` | Applies to AI and user shell paths |
| Tune model behavior | `chat.params` | Temperature, top-p, model options |
| Add provider headers | `chat.headers` | Observability, trace IDs, org headers |
| Rewrite system instructions | `experimental.chat.system.transform` | Keep this deterministic |
| Rewrite message history | `experimental.chat.messages.transform` | Use sparingly; high impact |
| Adjust tool docs/schema seen by model | `tool.definition` | Great for custom guidance |
| Observe lifecycle for metrics/alerts | `event` | Filter by `event.type` |
| Customize compaction prompt | `experimental.session.compacting` | Use `output.prompt` to replace entirely |

## Core Hooks for Runtime Control

| Hook | Input | Output | Typical Use |
|------|-------|--------|-------------|
| `tool.execute.before` | `{ tool, sessionID, callID }` | `{ args }` | Validate or rewrite tool args before execution |
| `tool.execute.after` | `{ tool, sessionID, callID, args }` | `{ title, output, metadata }` | Redact or annotate tool outputs |
| `shell.env` | `{ cwd, sessionID?, callID? }` | `{ env }` | Inject environment variables for shell runs |
| `tool.definition` | `{ toolID }` | `{ description, parameters }` | Modify tool schema/description shown to model |
| `permission.ask` | permission object | `{ status }` | Programmatically allow/ask/deny permission requests |
| `event` | `{ event }` | n/a | Subscribe to global emitted events |

## Additional Practical Hooks

| Hook | Input | Output | Typical Use |
|------|-------|--------|-------------|
| `chat.message` | session/model/message metadata | message + parts | Inject or normalize user/context parts pre-processing |
| `chat.params` | session/agent/model/provider/message | sampling/options | Set temperature/top-p/max tokens/provider options |
| `chat.headers` | session/agent/model/provider/message | headers map | Add trace or governance headers |
| `command.execute.before` | command/session/arguments | parts | Rewrite slash-command payload before execution |

## Event Hook: What You Can Observe

The `event` hook receives emitted runtime bus events. Common event groups include:

- Session: `session.created`, `session.updated`, `session.status`, `session.idle`, `session.diff`, `session.error`, `session.compacted`
- Message: `message.updated`, `message.part.updated`, `message.part.removed`, `message.removed`
- Tool: `tool.execute.before`, `tool.execute.after`
- Permission: `permission.asked`, `permission.replied`
- Command/TUI: `command.executed`, `tui.command.execute`, `tui.prompt.append`, `tui.toast.show`
- File/LSP/Todo: `file.edited`, `file.watcher.updated`, `lsp.updated`, `lsp.client.diagnostics`, `todo.updated`

Minimal pattern:

```ts
export const EventAudit: Plugin = async () => {
  return {
    event: async ({ event }) => {
      if (event.type === "session.error") {
        // send notification or structured log
      }
    },
  }
}
```

## Advanced and Experimental Hooks

| Hook | Output Mutation |
|------|-----------------|
| `experimental.chat.system.transform` | mutate `output.system: string[]` |
| `experimental.chat.messages.transform` | mutate `output.messages` |
| `experimental.session.compacting` | append `output.context[]` or replace with `output.prompt` |
| `experimental.compaction.autocontinue` | toggle `output.enabled` |
| `experimental.text.complete` | mutate generated text completion payload |

Treat `experimental.*` as unstable surfaces. Keep logic guarded and easy to disable.

## How To Use Hooks Correctly

1. Start with one hook and one policy.
2. Scope conditions narrowly (tool ID, path prefix, command prefix, event type).
3. Mutate only required `output` fields.
4. Keep hook execution fast and deterministic.
5. Add fallback behavior for missing fields in input/output payloads.
6. Validate with a small prompt and inspect logs before widening scope.

## Guardrail Example (.env protection)

```ts
export const EnvProtection: Plugin = async () => {
  return {
    "tool.execute.before": async (input, output) => {
      if (input.tool === "read" && typeof output.args?.filePath === "string") {
        if (output.args.filePath.includes(".env")) {
          throw new Error("Do not read .env files")
        }
      }
    },
  }
}
```

## Environment Injection Example

```ts
export const InjectEnv: Plugin = async () => {
  return {
    "shell.env": async (input, output) => {
      output.env.PROJECT_ROOT = input.cwd
      output.env.OPENCODE_FEATURE_FLAG = "1"
    },
  }
}
```

## Output Redaction Example

```ts
export const RedactSecrets: Plugin = async () => {
  return {
    "tool.execute.after": async (_input, output) => {
      output.output = output.output.replaceAll(/sk-[A-Za-z0-9_-]+/g, "sk-REDACTED")
    },
  }
}
```

## Hook Design Rules

1. Prefer deterministic, side-effect-light hooks.
2. Fail closed for sensitive operations.
3. Keep hooks fast; avoid long blocking operations.
4. Keep logs free of secrets.
5. Isolate one policy per plugin when possible.

## Verification Checklist

- Plugin file is in `.opencode/plugins/`.
- Exported symbol is a valid plugin function.
- OpenCode restarted after changes.
- Expected hook events appear in logs (`tool.execute.before/after`, `session.*`, etc.).
- Behavior is validated with a short reproducible prompt.
