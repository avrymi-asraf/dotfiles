/**
 * Demonstrates: block sensitive `.env` file reads in `tool.execute.before`.
 * Experimental API: No.
 * Sources: https://opencode.ai/docs/plugins | https://github.com/anomalyco/opencode/blob/main/packages/plugin/src/index.ts
 */
import type { Plugin } from "@opencode-ai/plugin"

export const ToolExecuteBeforeBlockEnvPlugin: Plugin = async () => ({
  "tool.execute.before": async (input, output) => {
    if (input.tool === "read" && typeof output.args?.filePath === "string" && output.args.filePath.includes(".env")) {
      throw new Error("Blocked by policy: reading .env files is not allowed")
    }
  },
})

