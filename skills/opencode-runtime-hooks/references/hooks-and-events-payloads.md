# OpenCode Runtime Hooks & Events Reference

Complete documentation of the OpenCode runtime execution flow, including all interception hooks (mutable) and state change events (read-only).

---

## Hooks vs Events

OpenCode uses two distinct mechanisms that must not be confused:

| Aspect | Hooks | Events |
|--------|-------|--------|
| **Purpose** | Interception points for mutation | State change notifications |
| **Mutability** | Output is mutable | Read-only observations |
| **Log representation** | Top-level `type` field | Nested inside `type: "event"` records |
| **Plugin interaction** | Plugins can modify behavior | Plugins can only observe |
| **Syntax** | Receives `(input, output)` | Emitted as notifications |

> **Critical**: Some names exist as BOTH a hook AND an event type (e.g., `tool.execute.before`). In debug logs, when you see `type: "tool.execute.before"`, that is the hook firing. If you see `type: "event"` with `event: "tool.execute.before"`, that is the event being observed through the `event` hook.

---

## Runtime Flow by Stage

### Stage 1: Session Initialization

```
Hook: config
  → Event: session.created
  → Event: session.updated
```

### Stage 2: User Message Entry

```
Hook: chat.message
  → Event: message.updated        (user message stored)
  → Event: message.part.updated   (user message part stored)
  → Event: session.updated        (session gets message reference)
  → Event: session.status         { type: "busy" }
```

### Stage 3: Title Generation (First Model Call)

```
Event: message.updated            (assistant placeholder created)
Hook: experimental.chat.system.transform   (title agent)
Hook: chat.params                 (title agent)
Hook: chat.headers                (title agent)
Hook: tool.definition             (fires once per available tool)
  → Event: session.updated        (title is set)
  → Event: session.diff           (diff summary)
```

### Stage 4: Main Agent Processing

```
Hook: experimental.chat.messages.transform
Hook: experimental.chat.system.transform   (main agent)
Hook: chat.params                 (main agent)
Hook: chat.headers                (main agent)
  → Event: session.status         { type: "busy" }
```

### Stage 5: Assistant Response Streaming

```
Event: message.part.updated       { type: "step-start" }
Event: message.part.updated       { type: "tool", state: "pending" }
```

### Stage 6: Tool Execution

```
Hook: tool.execute.before
  → Event: message.part.updated   { state: "running" }
  → Event: message.part.updated   { state: "running", metadata: { output: ... } }
Hook: tool.execute.after
  → Event: message.part.updated   { state: "completed" | "error" }
  → Event: message.part.updated   { type: "step-finish" }
```

### Stage 7: Text Response Streaming

```
Event: message.part.updated       { type: "text" }
Event: message.part.delta         { text: "...", delta: "..." }
```

### Stage 8: Completion

```
Event: message.updated            (assistant message finalized)
Event: session.status             { type: "idle" } | { type: "busy" } (if more turns)
Event: session.updated            (final session state)
```

### Stage 9: Subagent Tasks

```
Parent Hook: tool.execute.before  (tool: "task")
  → Child Event: session.created  { parentID: "..." }
  → Child: Runs full lifecycle independently
Parent Hook: tool.execute.after   (tool: "task")
```

---

## Hook Payload Reference

### `config`

Fires during session initialization to emit resolved configuration.

| Property | Type | Description |
|----------|------|-------------|
| `input` | `object` | Resolved configuration including plugins, agents, permissions |
| `output` | `object` | Same shape as input |

**Mutability**: The entire configuration object can be mutated.

**Example**:
```typescript
// Modify default agent settings
output.agents.default.model = "claude-sonnet-4";
output.agents.default.options.temperature = 0.7;
```

---

### `chat.message`

Intercepts user messages before processing begins.

**Input Shape**:

| Field | Type | Description |
|-------|------|-------------|
| `sessionID` | `string` | Unique session identifier |
| `agent` | `string` | Agent ID handling the message |
| `message` | `object` | Message metadata |
| `message.id` | `string` | Message UUID |
| `message.role` | `"user"` | Always "user" for this hook |
| `message.sessionID` | `string` | Session reference |
| `message.time` | `number` | Unix timestamp (ms) |
| `message.agent` | `string` | Target agent ID |
| `message.model` | `string` | Model ID |
| `parts` | `Array<MessagePart>` | Message content parts |

**Output Shape**:

| Field | Type | Mutable | Description |
|-------|------|---------|-------------|
| `parts` | `Array<MessagePart>` | ✅ Yes | Message content parts |

**When It Fires**: Stage 2 — immediately after user submits a message.

**Example Mutation**:
```typescript
// Add a system instruction part before user content
output.parts.unshift({
  type: "text",
  text: "[The user is asking about their own codebase.]"
});
```

---

### `experimental.chat.system.transform`

Transforms system prompt fragments before they are sent to the model.

**Input Shape**:

| Field | Type | Description |
|-------|------|-------------|
| `sessionID` | `string` | Session identifier |
| `model` | `object` | Full model descriptor |
| `model.id` | `string` | Model ID |
| `model.providerID` | `string` | Provider identifier |
| `model.name` | `string` | Human-readable model name |
| `model.family` | `string` | Model family |
| `model.api` | `string` | API type |
| `model.status` | `string` | Model status |
| `model.headers` | `object` | Default headers |
| `model.options` | `object` | Default options |
| `model.cost` | `object` | Pricing info |
| `model.limit` | `object` | Token limits |
| `model.capabilities` | `Array<string>` | Model capabilities |
| `model.release_date` | `string` | Release date |
| `model.variants` | `Array<object>` | Model variants |

**Output Shape**:

| Field | Type | Mutable | Description |
|-------|------|---------|-------------|
| `system` | `Array<string>` | ✅ Yes | System prompt fragments |

**When It Fires**: Stage 3 (title generation) and Stage 4 (main agent), before each model call.

**Example Mutation**:
```typescript
// Add a custom instruction to the system prompt
output.system.push("Always explain your reasoning before giving code.");

// Or replace entirely
output.system = output.system.filter(s => !s.includes("old instruction"));
```

---

### `experimental.chat.messages.transform`

Rewrites the entire message history before the main agent model call.

**Input Shape**:

| Field | Type | Description |
|-------|------|-------------|
| (minimal/empty) | `object` | Often empty or contains session context |

**Output Shape**:

| Field | Type | Mutable | Description |
|-------|------|---------|-------------|
| `messages` | `Array<Message>` | ✅ Yes | Complete message history |

**When It Fires**: Stage 4 — before main agent processing.

**Example Mutation**:
```typescript
// Inject a summary message at the start
output.messages.unshift({
  role: "system",
  content: "Previous context: The user is working on a React app."
});

// Remove tool call/response pairs for compaction
output.messages = output.messages.filter(m => m.role !== "tool");
```

---

### `chat.params`

Modulates generation parameters for model calls.

**Input Shape**:

| Field | Type | Description |
|-------|------|-------------|
| `sessionID` | `string` | Session identifier |
| `agent` | `string` | Agent ID |
| `model` | `object` | Model descriptor (see `experimental.chat.system.transform`) |
| `provider` | `object` | Provider configuration |
| `message` | `object` | Current message context |

**Output Shape**:

| Field | Type | Mutable | Description |
|-------|------|---------|-------------|
| `temperature` | `number` | ✅ Yes | Sampling temperature |
| `maxOutputTokens` | `number` | ✅ Yes | Maximum output tokens |
| `options` | `object` | ✅ Yes | Additional model options |

**When It Fires**: Stage 3 (title generation) and Stage 4 (main agent).

**Example Mutation**:
```typescript
// Lower temperature for title generation (more deterministic)
if (input.agent === "title") {
  output.temperature = 0.1;
  output.maxOutputTokens = 50;
}

// Increase token limit for code generation
if (input.message.content?.includes("```")) {
  output.maxOutputTokens = 8000;
}
```

---

### `chat.headers`

Injects or modifies HTTP headers for model API requests.

**Input Shape**:

| Field | Type | Description |
|-------|------|-------------|
| `sessionID` | `string` | Session identifier |
| `agent` | `string` | Agent ID |
| `model` | `object` | Model descriptor |
| `provider` | `object` | Provider configuration |
| `message` | `object` | Current message context |

**Output Shape**:

| Field | Type | Mutable | Description |
|-------|------|---------|-------------|
| `headers` | `object` | ✅ Yes | HTTP headers to send |

**When It Fires**: Stage 3 (title generation) and Stage 4 (main agent), just before API request.

**Example Mutation**:
```typescript
// Add custom tracing header
output.headers["X-Request-ID"] = `session-${input.sessionID}`;

// Add auth token from environment
output.headers["Authorization"] = `Bearer ${process.env.CUSTOM_API_KEY}`;
```

---

### `tool.definition`

Intercepts each tool's schema before it is shown to the model.

**Input Shape**:

| Field | Type | Description |
|-------|------|-------------|
| `toolID` | `string` | Tool identifier |

**Output Shape**:

| Field | Type | Mutable | Description |
|-------|------|---------|-------------|
| `description` | `string` | ✅ Yes | Tool description shown to model |
| `parameters` | `object` | ✅ Yes | JSON Schema for tool arguments |

**When It Fires**: Stage 3 — once per available tool during title generation context setup.

**Example Mutation**:
```typescript
// Enhance description for better model understanding
if (input.toolID === "shell") {
  output.description += "\nPrefer using absolute paths. Avoid destructive commands.";
}

// Add required field
output.parameters.required = [...(output.parameters.required || []), "reasoning"];
```

---

### `tool.execute.before`

Intercepts tool execution before the tool runs.

**Input Shape**:

| Field | Type | Description |
|-------|------|-------------|
| `tool` | `string` | Tool identifier |
| `sessionID` | `string` | Session identifier |
| `callID` | `string` | Unique call identifier |
| `args` | `object` | Arguments passed to the tool |

**Output Shape**:

| Field | Type | Mutable | Description |
|-------|------|---------|-------------|
| `args` | `object` | ✅ Yes | Arguments passed to the tool |

**When It Fires**: Stage 6 — when the model requests a tool call.

**Behavior**:
- Mutate `output.args` to validate, modify, or transform arguments
- Throw an error to hard-stop execution

**Example Mutation**:
```typescript
// Validate and sanitize shell commands
if (input.tool === "shell") {
  const cmd = input.args.command;
  if (cmd.includes("rm -rf /")) {
    throw new Error("Destructive command blocked");
  }
  output.args.command = cmd.replace(/\bgit push\b/, "git push --dry-run");
}

// Add metadata to file reads
if (input.tool === "read") {
  output.args.includeLineNumbers = true;
}
```

---

### `tool.execute.after`

Intercepts tool results before they are returned to the model.

**Input Shape**:

| Field | Type | Description |
|-------|------|-------------|
| `tool` | `string` | Tool identifier |
| `sessionID` | `string` | Session identifier |
| `callID` | `string` | Unique call identifier |
| `args` | `object` | Original arguments passed to the tool |

**Output Shape**:

| Field | Type | Mutable | Description |
|-------|------|---------|-------------|
| `title` | `string` | ✅ Yes | Display title for the tool result |
| `output` | `any` | ✅ Yes | Tool result data |
| `metadata` | `object` | ✅ Yes | Additional metadata |

**When It Fires**: Stage 6 — after tool execution completes.

**Example Mutation**:
```typescript
// Redact sensitive information from output
if (input.tool === "env") {
  output.output = output.output.replace(/API_KEY=[^\n]+/g, "API_KEY=***");
}

// Add annotations
output.metadata = {
  ...output.metadata,
  processedBy: "my-plugin",
  timestamp: Date.now()
};

// Transform large outputs
if (JSON.stringify(output.output).length > 10000) {
  output.output = {
    summary: "Output too large, truncated",
    length: JSON.stringify(output.output).length,
    preview: JSON.stringify(output.output).slice(0, 500) + "..."
  };
}
```

---

### `shell.env`

Injects environment variables for shell tool executions.

**Input Shape**:

| Field | Type | Description |
|-------|------|-------------|
| `cwd` | `string` | Current working directory |
| `sessionID` | `string \| undefined` | Session identifier (optional) |
| `callID` | `string \| undefined` | Call identifier (optional) |

**Output Shape**:

| Field | Type | Mutable | Description |
|-------|------|---------|-------------|
| `env` | `object` | ✅ Yes | Environment variables to inject |

**When It Fires**: Whenever the `shell` tool executes.

**Example Mutation**:
```typescript
// Add project-specific env vars
output.env["NODE_ENV"] = "development";
output.env["PROJECT_ROOT"] = input.cwd;

// Inject secrets from secure storage
output.env["API_TOKEN"] = await getSecret("api-token");
```

---

### `permission.ask`

Programmatically handles permission requests.

**Input Shape**:

| Field | Type | Description |
|-------|------|-------------|
| `type` | `string` | Permission type (e.g., "shell", "file", "network") |
| `resource` | `string` | Resource being accessed |
| `action` | `string` | Action being requested |
| `sessionID` | `string` | Session identifier |
| `metadata` | `object` | Additional context |

**Output Shape**:

| Field | Type | Mutable | Description |
|-------|------|---------|-------------|
| `status` | `"allow" \| "ask" \| "deny"` | ✅ Yes | Permission decision |

**When It Fires**: Whenever the runtime needs to request a permission.

**Example Mutation**:
```typescript
// Auto-allow safe directories
if (input.type === "file" && input.resource.startsWith("/home/user/project")) {
  output.status = "allow";
}

// Auto-deny dangerous commands
if (input.type === "shell" && input.action.includes("rm -rf")) {
  output.status = "deny";
}
```

---

### `command.execute.before`

Intercepts slash command execution.

**Input Shape**:

| Field | Type | Description |
|-------|------|-------------|
| `command` | `string` | Command name (without leading `/`) |
| `session` | `object` | Session context |
| `arguments` | `Array<string>` | Command arguments |
| `parts` | `Array<Part>` | Message parts |

**Output Shape**:

| Field | Type | Mutable | Description |
|-------|------|---------|-------------|
| `parts` | `Array<Part>` | ✅ Yes | Rewritten message parts |

**When It Fires**: When a user sends a message starting with `/`.

**Example Mutation**:
```typescript
// Transform /summarize command into a system instruction
if (input.command === "summarize") {
  output.parts = [{
    type: "text",
    text: "Please summarize the following: " + input.arguments.join(" ")
  }];
}
```

---

### `event`

Subscribe to all runtime events for observation.

**Input Shape**:

| Field | Type | Description |
|-------|------|-------------|
| `event` | `object` | The event payload (varies by event type) |
| `event.type` | `string` | Event type name |

**Output Shape**:

| Field | Type | Mutable | Description |
|-------|------|---------|-------------|
| N/A | — | ❌ No | Events are read-only |

**When It Fires**: Every time any event is emitted.

**Example Usage**:
```typescript
// Log all events for debugging
console.log(`[${input.event.type}]`, JSON.stringify(input.event, null, 2));

// Track specific event patterns
if (input.event.type === "session.status" && input.event.status === "busy") {
  metrics.recordSessionBusy(input.event.sessionID);
}
```

---

### `experimental.session.compacting`

Customizes session context compaction behavior.

**Input Shape**:

| Field | Type | Description |
|-------|------|-------------|
| `sessionID` | `string` | Session identifier |

**Output Shape**:

| Field | Type | Mutable | Description |
|-------|------|---------|-------------|
| `context` | `Array<Message>` | ✅ Yes | Compacted message context |
| `prompt` | `string \| undefined` | ✅ Yes | Optional compaction prompt |

**When It Fires**: When the runtime compacts session context to fit token limits.

**Example Mutation**:
```typescript
// Preserve important messages during compaction
const importantIds = ["msg-1", "msg-5"];
output.context = input.context.filter(m => importantIds.includes(m.id));

// Add custom compaction instruction
output.prompt = "Summarize while preserving all file paths and function names.";
```

---

### `experimental.compaction.autocontinue`

Controls whether the runtime auto-continues after compaction.

**Input Shape**:

| Field | Type | Description |
|-------|------|-------------|
| `context` | `Array<Message>` | Messages being compacted |
| `sessionID` | `string` | Session identifier |

**Output Shape**:

| Field | Type | Mutable | Description |
|-------|------|---------|-------------|
| `enabled` | `boolean` | ✅ Yes | Whether to auto-continue |

**When It Fires**: After session compaction, before deciding to continue.

**Example Mutation**:
```typescript
// Disable auto-continue for sensitive sessions
if (input.sessionID.includes("private")) {
  output.enabled = false;
}
```

---

### `experimental.text.complete`

Intercepts text completion requests.

**Input Shape**:

| Field | Type | Description |
|-------|------|-------------|
| `text` | `string` | Text being completed |
| `context` | `object` | Completion context |
| `sessionID` | `string` | Session identifier |

**Output Shape**:

| Field | Type | Mutable | Description |
|-------|------|---------|-------------|
| `text` | `string` | ✅ Yes | Modified completion text |
| `options` | `object` | ✅ Yes | Completion options |

**When It Fires**: During text completion operations.

**Example Mutation**:
```typescript
// Inject context into completion
output.text = `In the context of this project: ${input.context.summary}\n\n${input.text}`;
```

---

## Event Payload Reference

Events are read-only state change notifications. They are only visible in debug logs when the `event` hook is enabled.

### `session.created`

Emitted when a new session is created.

| Field | Type | Description |
|-------|------|-------------|
| `type` | `"session.created"` | Event type |
| `sessionID` | `string` | Unique session identifier |
| `project` | `object` | Project information |
| `permissions` | `Array<string>` | Granted permissions |
| `parentID` | `string \| undefined` | Parent session ID (for subagents) |

**Lifecycle Position**: Stage 1 — after `config` hook.

---

### `session.updated`

Emitted when session metadata changes.

| Field | Type | Description |
|-------|------|-------------|
| `type` | `"session.updated"` | Event type |
| `sessionID` | `string` | Session identifier |
| `updates` | `object` | Changed fields |

**Lifecycle Position**: Stages 1, 2, 3, 8.

---

### `session.status`

Emitted when session status changes.

| Field | Type | Description |
|-------|------|-------------|
| `type` | `"session.status"` | Event type |
| `sessionID` | `string` | Session identifier |
| `status` | `"idle" \| "busy"` | New status |

**Lifecycle Position**: Stages 2, 4, 8.

**Related Hooks**: Fires after `chat.message` (busy), during processing (busy), and on completion (idle).

---

### `session.diff`

Emitted with a diff summary of session changes.

| Field | Type | Description |
|-------|------|-------------|
| `type` | `"session.diff"` | Event type |
| `sessionID` | `string` | Session identifier |
| `diff` | `object` | Diff summary |

**Lifecycle Position**: Stage 3 — after title generation.

---

### `message.updated`

Emitted when a message is stored or updated.

| Field | Type | Description |
|-------|------|-------------|
| `type` | `"message.updated"` | Event type |
| `messageID` | `string` | Message identifier |
| `sessionID` | `string` | Session identifier |
| `role` | `"user" \| "assistant"` | Message role |
| `content` | `string \| undefined` | Message content |

**Lifecycle Position**: Stages 2 (user message), 3 (assistant placeholder), 8 (assistant finalized).

---

### `message.part.updated`

Emitted when a message part is created or updated.

| Field | Type | Description |
|-------|------|-------------|
| `type` | `"message.part.updated"` | Event type |
| `partID` | `string` | Part identifier |
| `messageID` | `string` | Parent message ID |
| `sessionID` | `string` | Session identifier |
| `partType` | `string` | Part type (`"text"`, `"tool"`, `"step-start"`, `"step-finish"`) |
| `state` | `string \| undefined` | Tool state (`"pending"`, `"running"`, `"completed"`, `"error"`) |
| `metadata` | `object \| undefined` | Additional metadata (e.g., streaming output) |

**Lifecycle Position**: Stages 2, 5, 6, 7.

**Related Hooks**: Surrounds `tool.execute.before` and `tool.execute.after`.

---

### `message.part.delta`

Emitted for incremental text streaming deltas.

| Field | Type | Description |
|-------|------|-------------|
| `type` | `"message.part.delta"` | Event type |
| `partID` | `string` | Part identifier |
| `messageID` | `string` | Parent message ID |
| `sessionID` | `string` | Session identifier |
| `text` | `string` | Current accumulated text |
| `delta` | `string` | New text delta |

**Lifecycle Position**: Stage 7 — during text streaming.

---

## Mutation Examples

### Example 1: Custom System Prompt Injection

```typescript
// In your plugin's onHook handler
onHook("experimental.chat.system.transform", (input, output) => {
  // Only modify for specific model
  if (input.model.id === "claude-sonnet") {
    output.system.push(
      "You are a helpful coding assistant specialized in TypeScript."
    );
  }
});
```

### Example 2: Dynamic Temperature Based on Content

```typescript
onHook("chat.params", (input, output) => {
  const content = JSON.stringify(input.message);
  
  // Lower temperature for factual/code queries
  if (content.includes("explain") || content.includes("how to")) {
    output.temperature = 0.3;
  }
  
  // Higher temperature for creative tasks
  if (content.includes("brainstorm") || content.includes("ideas")) {
    output.temperature = 0.9;
  }
});
```

### Example 3: Tool Argument Validation

```typescript
onHook("tool.execute.before", (input, output) => {
  if (input.tool === "shell") {
    const blocked = ["rm -rf", "> /dev/null", "curl | bash"];
    const cmd = input.args.command;
    
    for (const pattern of blocked) {
      if (cmd.includes(pattern)) {
        throw new Error(`Blocked dangerous command pattern: ${pattern}`);
      }
    }
    
    // Add safety flag
    output.args.command = `set -euo pipefail; ${cmd}`;
  }
});
```

### Example 4: Output Transformation

```typescript
onHook("tool.execute.after", (input, output) => {
  if (input.tool === "search") {
    // Limit result size
    const results = output.output.results || [];
    if (results.length > 10) {
      output.output = {
        ...output.output,
        results: results.slice(0, 10),
        truncated: true,
        totalCount: results.length
      };
    }
  }
});
```

### Example 5: Event Logging Plugin

```typescript
onHook("event", (input) => {
  // All events are read-only — just observe
  const { event } = input;
  
  console.log(`[${event.type}]`, {
    sessionID: event.sessionID,
    timestamp: new Date().toISOString()
  });
  
  // Track metrics
  if (event.type === "tool.execute.after") {
    metrics.recordToolCall(event.tool, event.duration);
  }
});
```

### Example 6: Message Part Rewriting

```typescript
onHook("chat.message", (input, output) => {
  // Add prefix to all user messages
  const parts = output.parts || [];
  
  if (parts.length > 0 && parts[0].type === "text") {
    parts[0].text = `[User message]: ${parts[0].text}`;
  }
  
  output.parts = parts;
});
```

---

## Quick Reference: Hook/Event Name Collisions

| Name | Hook | Event |
|------|------|-------|
| `tool.execute.before` | ✅ Intercepts args before execution | ✅ Notified via `event` hook as read-only |
| `tool.execute.after` | ✅ Intercepts results after execution | ✅ Notified via `event` hook as read-only |
| `session.updated` | ❌ Not a hook | ✅ Event only |
| `message.updated` | ❌ Not a hook | ✅ Event only |

When in doubt:
- **Hook** = top-level `type` in debug logs, receives `(input, output)`, can mutate
- **Event** = nested inside `type: "event"` records, read-only, observed through `event` hook
