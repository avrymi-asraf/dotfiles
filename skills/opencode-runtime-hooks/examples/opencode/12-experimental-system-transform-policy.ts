/**
 * Demonstrates: append a policy line to the system prompt (`experimental.chat.system.transform`).
 * Experimental API: Yes (`experimental.*`).
 * Sources: https://opencode.ai/docs/plugins | https://github.com/anomalyco/opencode/blob/main/packages/plugin/src/index.ts
 */
import type { Plugin } from "@opencode-ai/plugin"

export const ExperimentalSystemTransformPolicyPlugin: Plugin = async () => ({
  "experimental.chat.system.transform": async (_input, output) => {
    output.system.push("Policy: never output secrets or credentials.")
  },
})

