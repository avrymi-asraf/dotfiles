/**
 * Demonstrates: add a safety hint to the bash tool definition (`tool.definition`).
 * Experimental API: No.
 * Sources: https://opencode.ai/docs/tools | https://github.com/anomalyco/opencode/blob/main/packages/plugin/src/index.ts
 */
import type { Plugin } from "@opencode-ai/plugin"

export const ToolDefinitionBashSafetyHintPlugin: Plugin = async () => ({
  "tool.definition": async (input, output) => {
    if (input.toolID === "bash") {
      output.description = `${output.description ?? ""}\nSafety: avoid destructive commands unless explicitly requested.`
    }
  },
})

