/**
 * Demonstrates: normalize tool arguments before execution (`tool.execute.before`).
 * Experimental API: No.
 * Sources: https://opencode.ai/docs/plugins | https://github.com/anomalyco/opencode/blob/main/packages/opencode/src/session/prompt.ts
 */
import type { Plugin } from "@opencode-ai/plugin"

export const ToolExecuteBeforeArgNormalizePlugin: Plugin = async () => ({
  "tool.execute.before": async (input, output) => {
    if (input.tool === "bash" && typeof output.args?.command === "string") {
      output.args.command = output.args.command.replace(/\s+/g, " ").trim()
    }
  },
})

