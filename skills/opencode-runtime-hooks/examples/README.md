# Runtime Hook Examples Index

Minimal, single-concept examples for:
- OpenCode plugin hooks
- VS Code extension event/hooks

## OpenCode examples (`examples/opencode`)

| File | What it demonstrates | Sources |
|---|---|---|
| `opencode/01-tool-execute-before-block-env.ts` | Block `.env` reads before tool execution. | Docs: https://opencode.ai/docs/plugins • Source: https://github.com/anomalyco/opencode/blob/main/packages/plugin/src/index.ts |
| `opencode/02-tool-execute-before-arg-normalize.ts` | Normalize tool args before execution. | Docs: https://opencode.ai/docs/plugins • Source: https://github.com/anomalyco/opencode/blob/main/packages/opencode/src/session/prompt.ts |
| `opencode/03-tool-execute-after-redact-output.ts` | Redact secrets in tool output after execution. | Docs: https://opencode.ai/docs/plugins • Source: https://github.com/anomalyco/opencode/blob/main/packages/plugin/src/index.ts |
| `opencode/04-tool-execute-after-add-metadata.ts` | Attach metadata to tool results. | Docs: https://opencode.ai/docs/plugins • Source: https://github.com/anomalyco/opencode/blob/main/packages/plugin/src/index.ts |
| `opencode/05-shell-env-inject-project-vars.ts` | Inject env vars for shell tool runs. | Docs: https://opencode.ai/docs/plugins • Source: https://github.com/anomalyco/opencode/blob/main/packages/plugin/src/index.ts |
| `opencode/06-event-log-session-errors.ts` | Observe events and log `session.error`. | Docs: https://opencode.ai/docs/plugins • Source: https://github.com/anomalyco/opencode/blob/main/packages/plugin/src/index.ts |
| `opencode/07-chat-params-force-low-temp.ts` | Force low model temperature. | Docs: https://opencode.ai/docs/plugins • Source: https://github.com/anomalyco/opencode/blob/main/packages/plugin/src/index.ts |
| `opencode/08-chat-headers-trace-id.ts` | Add trace ID request header. | Docs: https://opencode.ai/docs/plugins • Source: https://github.com/anomalyco/opencode/blob/main/packages/plugin/src/index.ts |
| `opencode/09-tool-definition-bash-safety-hint.ts` | Add safety guidance to bash tool definition. | Docs: https://opencode.ai/docs/tools • Source: https://github.com/anomalyco/opencode/blob/main/packages/plugin/src/index.ts |
| `opencode/10-command-execute-before-rewrite.ts` | Rewrite slash-command input before execution. | Docs: https://opencode.ai/docs/plugins • Source: https://github.com/anomalyco/opencode/blob/main/packages/plugin/src/index.ts |
| `opencode/11-permission-ask-policy.ts` | Programmatic allow/ask policy in `permission.ask`. | Docs: https://opencode.ai/docs/config • Source: https://github.com/anomalyco/opencode/blob/main/packages/plugin/src/index.ts |
| `opencode/12-experimental-system-transform-policy.ts` | **Experimental**: append system policy line. | Docs: https://opencode.ai/docs/plugins • Source: https://github.com/anomalyco/opencode/blob/main/packages/plugin/src/index.ts |
| `opencode/13-experimental-messages-transform-trim.ts` | **Experimental**: trim message history. | Docs: https://opencode.ai/docs/plugins • Source: https://github.com/anomalyco/opencode/blob/main/packages/plugin/src/index.ts |
| `opencode/14-experimental-session-compacting-custom.ts` | **Experimental**: customize compaction context/prompt. | Docs: https://opencode.ai/docs/plugins • Source: https://github.com/anomalyco/opencode/blob/main/packages/plugin/src/index.ts |
| `opencode/15-experimental-compaction-autocontinue-off.ts` | **Experimental**: disable compaction auto-continue. | Docs: https://opencode.ai/docs/plugins • Source: https://github.com/anomalyco/opencode/blob/main/packages/plugin/src/index.ts |

