/**
 * Demonstrates: implement a small permission policy in `permission.ask`.
 * Experimental API: No.
 * Sources: https://opencode.ai/docs/config | https://github.com/anomalyco/opencode/blob/main/packages/plugin/src/index.ts
 */
import type { Plugin } from "@opencode-ai/plugin"

export const PermissionAskPolicyPlugin: Plugin = async () => ({
  "permission.ask": async (input, output) => {
    if (input.tool === "bash" && typeof input.command === "string" && input.command.startsWith("git status")) {
      output.status = "allow"
      return
    }
    output.status = "ask"
  },
})

