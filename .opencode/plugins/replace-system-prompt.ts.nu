import { appendFileSync } from "node:fs";
import { join } from "node:path";

/** @typedef {import("@opencode-ai/plugin").Plugin} Plugin */

// Helper to safely serialize objects with circular references
const safeStringify = (obj) => {
  const seen = new WeakSet();
  return JSON.stringify(obj, (key, value) => {
    if (typeof value === "object" && value !== null) {
      if (seen.has(value)) {
        return "[Circular Reference]";
      }
      seen.add(value);
    }
    return value;
  });
};

/** @type {Plugin} */
export const SlimPromptPlugin = async (ctx) => {
  // Save the JSONL file in the project root directory
  const jsonlPath = join(ctx.directory || process.cwd(), "opencode-debug.jsonl");
  
  console.log(`[Plugin Debug] SlimPromptPlugin loaded. Logging to: ${jsonlPath}`);

  const writeToJsonl = (eventType, payload) => {
    try {
      const entry = {
        timestamp: new Date().toISOString(),
        type: eventType,
        payload: payload
      };
      appendFileSync(jsonlPath, safeStringify(entry) + "\n", "utf8");
    } catch (e) {
      console.error("[Plugin Debug] Failed to write to JSONL:", e.message);
    }
  };

  const logHook = (hookName) => async (...args) => {
    // Write to JSONL
    writeToJsonl(hookName, args);
  };

  return {
    // "experimental.chat.system.transform":logHook("experimental.chat.system.transform"),
    // "tool.execute.before": logHook("tool.execute.before"),
    // "tool.execute.after": logHook("tool.execute.after"),
    "event": logHook("event")
    // "chat.message": logHook("chat.message"),
    // "chat.request": logHook("chat.request"),
    // "chat.response": logHook("chat.response"),
    // "session.start": logHook("session.start"),
    // "session.idle": logHook("session.idle")
  };
};

export default SlimPromptPlugin;
