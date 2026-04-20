/**
 * Demonstrates: add metadata to tool results (`tool.execute.after`).
 * Experimental API: No.
 * Sources: https://opencode.ai/docs/plugins | https://github.com/anomalyco/opencode/blob/main/packages/plugin/src/index.ts
 */
import type { Plugin } from "@opencode-ai/plugin"

export const ToolExecuteAfterAddMetadataPlugin: Plugin = async () => ({
  "tool.execute.after": async (input, output) => {
    output.metadata = {
      ...(output.metadata ?? {}),
      reviewedBy: "ToolExecuteAfterAddMetadataPlugin",
      tool: input.tool,
    }
  },
})

