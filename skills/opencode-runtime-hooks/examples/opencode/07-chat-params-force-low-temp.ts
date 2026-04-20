/**
 * Demonstrates: force low-temperature model sampling (`chat.params`).
 * Experimental API: No.
 * Sources: https://opencode.ai/docs/plugins | https://github.com/anomalyco/opencode/blob/main/packages/plugin/src/index.ts
 */
import type { Plugin } from "@opencode-ai/plugin"

export const ChatParamsForceLowTempPlugin: Plugin = async () => ({
  "chat.params": async (_input, output) => {
    output.temperature = 0.1
  },
})

