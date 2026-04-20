/**
 * Demonstrates: add a trace header to model-provider requests (`chat.headers`).
 * Experimental API: No.
 * Sources: https://opencode.ai/docs/plugins | https://github.com/anomalyco/opencode/blob/main/packages/plugin/src/index.ts
 */
import type { Plugin } from "@opencode-ai/plugin"

export const ChatHeadersTraceIdPlugin: Plugin = async () => ({
  "chat.headers": async (input, output) => {
    output["x-trace-id"] = input.sessionID ?? "unknown-session"
  },
})

