/**
 * Demonstrates: redact sensitive output after tool execution (`tool.execute.after`).
 * Experimental API: No.
 * Sources: https://opencode.ai/docs/plugins | https://github.com/anomalyco/opencode/blob/main/packages/plugin/src/index.ts
 */
import type { Plugin } from "@opencode-ai/plugin"

export const ToolExecuteAfterRedactOutputPlugin: Plugin = async () => ({
  "tool.execute.after": async (_input, output) => {
    if (typeof output.output === "string") {
      output.output = output.output.replaceAll(/sk-[A-Za-z0-9_-]+/g, "sk-REDACTED")
    }
  },
})

