/**
 * Demonstrates: customize compaction context/prompt (`experimental.session.compacting`).
 * Experimental API: Yes (`experimental.*`).
 * Sources: https://opencode.ai/docs/plugins | https://github.com/anomalyco/opencode/blob/main/packages/plugin/src/index.ts
 */
import type { Plugin } from "@opencode-ai/plugin"

export const ExperimentalSessionCompactingCustomPlugin: Plugin = async () => ({
  "experimental.session.compacting": async (_input, output) => {
    output.context.push("Keep unresolved TODO items and blocking errors.")
    output.prompt = "Create a short summary focused on decisions, TODOs, and blockers."
  },
})

