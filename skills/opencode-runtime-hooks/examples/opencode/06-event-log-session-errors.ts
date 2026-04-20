/**
 * Demonstrates: observe runtime events and log only `session.error`.
 * Experimental API: No.
 * Sources: https://opencode.ai/docs/plugins | https://github.com/anomalyco/opencode/blob/main/packages/plugin/src/index.ts
 */
import type { Plugin } from "@opencode-ai/plugin"

export const EventLogSessionErrorsPlugin: Plugin = async () => ({
  event: async ({ event }) => {
    if (event.type === "session.error") {
      console.error("[opencode][session.error]", event.properties)
    }
  },
})

