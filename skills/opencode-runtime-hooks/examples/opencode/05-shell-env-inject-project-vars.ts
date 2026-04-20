/**
 * Demonstrates: inject project-scoped env vars for shell runs (`shell.env`).
 * Experimental API: No.
 * Sources: https://opencode.ai/docs/plugins | https://github.com/anomalyco/opencode/blob/main/packages/plugin/src/index.ts
 */
import type { Plugin } from "@opencode-ai/plugin"

export const ShellEnvInjectProjectVarsPlugin: Plugin = async () => ({
  "shell.env": async (input, output) => {
    output.env.PROJECT_ROOT = input.cwd
    output.env.OPENCODE_EXAMPLE = "true"
  },
})

