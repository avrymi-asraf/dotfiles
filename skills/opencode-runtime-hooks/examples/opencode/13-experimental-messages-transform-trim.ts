/**
 * Demonstrates: trim chat history to the most recent messages (`experimental.chat.messages.transform`).
 * Experimental API: Yes (`experimental.*`).
 * Sources: https://opencode.ai/docs/plugins | https://github.com/anomalyco/opencode/blob/main/packages/plugin/src/index.ts
 */
import type { Plugin } from "@opencode-ai/plugin"

export const ExperimentalMessagesTransformTrimPlugin: Plugin = async () => ({
  "experimental.chat.messages.transform": async (_input, output) => {
    output.messages = output.messages.slice(-10)
  },
})

