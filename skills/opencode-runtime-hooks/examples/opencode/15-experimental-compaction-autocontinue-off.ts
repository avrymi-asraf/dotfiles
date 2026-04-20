/**
 * Demonstrates: disable synthetic auto-continue after compaction (`experimental.compaction.autocontinue`).
 * Experimental API: Yes (`experimental.*`).
 * Sources: https://opencode.ai/docs/plugins | https://github.com/anomalyco/opencode/blob/main/packages/plugin/src/index.ts
 */
import type { Plugin } from "@opencode-ai/plugin"

export const ExperimentalCompactionAutocontinueOffPlugin: Plugin = async () => ({
  "experimental.compaction.autocontinue": async (_input, output) => {
    output.enabled = false
  },
})

