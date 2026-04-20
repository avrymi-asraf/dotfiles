/**
 * Demonstrates: rewrite slash-command parts before execution (`command.execute.before`).
 * Experimental API: No.
 * Sources: https://opencode.ai/docs/plugins | https://github.com/anomalyco/opencode/blob/main/packages/plugin/src/index.ts
 */
import type { Plugin } from "@opencode-ai/plugin"

export const CommandExecuteBeforeRewritePlugin: Plugin = async () => ({
  "command.execute.before": async (input, output) => {
    if (input.command === "summarize") {
      output.parts = [{ type: "text", text: "Summarize in 3 bullets max." }, ...(output.parts ?? [])]
    }
  },
})

