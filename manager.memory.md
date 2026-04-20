# Manager Memory

## Current Task
Improve the `opencode-runtime-hooks` skill by analyzing the two debug JSONL files and creating clear documentation about:
1. The flow of running an agent (what happens step-by-step)
2. What hooks and events fire at every stage
3. What payloads exist in every hook/event
4. How each payload can be changed/mutated

## Analysis Completed

### Files Read
- `skills/opencode-runtime-hooks/SKILL.md` - main skill file (283 lines)
- `skills/opencode-runtime-hooks/references/runtime-sequence.md` - event sequencing reference
- `skills/opencode-runtime-hooks/references/hooks-reference.md` - hook signatures reference
- `skills/opencode-runtime-hooks/examples/README.md` - examples index
- `skills/opencode-runtime-hooks/examples/opencode/*.ts` - example plugins
- `skills/opencode-runtime-hooks/references/opencode-debug-with-events.jsonl` - debug log WITH event hook enabled
- `skills/opencode-runtime-hooks/references/opencode-debug-no-events.jsonl` - debug log WITHOUT event hook
- `.opencode/plugins/all-events.ts.nu` - the plugin that generated the logs

### Key Discovery: Hooks vs Events
The two JSONL files reveal a critical distinction that the current skill blurs:

**Hooks** (interception points):
- Appear as top-level `type` values in the debug log
- Plugins register handlers for these to MUTATE behavior
- Examples: `tool.execute.before`, `tool.execute.after`, `chat.params`, `chat.headers`, `experimental.chat.system.transform`, `experimental.chat.messages.transform`, `tool.definition`, `chat.message`, `config`
- Each hook receives `(input, output)` where `output` can be mutated

**Events** (state change notifications):
- Appear ONLY when the `event` hook is enabled, nested inside `type: "event"` records
- These are emitted BY the runtime to notify observers
- Examples: `session.created`, `session.updated`, `session.status`, `message.updated`, `message.part.updated`, `message.part.delta`, `session.diff`
- The `event` hook can subscribe to these but they are read-only notifications

**Both**: Some things exist as both a hook AND an event type (e.g., `tool.execute.before`)

### Runtime Flow (from logs)

**Simple request flow** (with-events.jsonl - "list all files"):
1. `config` hook - resolved configuration
2. `session.created` event - new session
3. `session.updated` event - session metadata
4. `chat.message` hook - user message enters
5. `message.updated` / `message.part.updated` events - message stored
6. `session.status` event -> busy
7. `message.updated` event - assistant message placeholder
8. `experimental.chat.system.transform` hook (title generation)
9. `chat.params` hook (title agent)
10. `chat.headers` hook (title agent)
11. `tool.definition` hooks for all tools
12. `session.updated` event - title set
13. `session.diff` event
14. `experimental.chat.messages.transform` hook
15. `experimental.chat.system.transform` hook (main agent)
16. `chat.params` / `chat.headers` hooks (main agent)
17. `session.status` event -> busy
18. `message.part.updated` event -> step-start
19. `message.part.updated` event -> tool pending
20. `tool.execute.before` hook - validate/modify args
21. `message.part.updated` event -> tool running
22. `message.part.updated` event -> tool running with output
23. `tool.execute.after` hook - modify output
24. `message.part.updated` event -> tool completed
25. `message.part.updated` event -> step-finish
26. `message.updated` events - finalize assistant message
27. `message.part.delta` events - text streaming
28. `session.status` events

**Complex request flow** (no-events.jsonl - manager with memory):
- Same pattern but with multiple turns
- Shows `tool.execute.before`/`after` for `read`, `todowrite`, `write`, `bash`
- Shows failed tool calls (read of missing file)
- Tool definitions re-sent on every turn

### Plan to Improve the Skill

1. **Create a new reference file** `references/hooks-and-events-payloads.md` that documents:
   - The complete runtime flow stage by stage
   - For each stage: which hooks fire, which events emit
   - Exact payload shapes for each hook (input and output)
   - Exact payload shapes for each event type
   - What fields are mutable in each hook
   - Examples of mutations

2. **Update `references/runtime-sequence.md`** to clearly distinguish hooks from events

3. **Update `SKILL.md`** to:
   - Add a clear section on "Hooks vs Events" 
   - Reference the new payload documentation
   - Improve the lifecycle analysis section with concrete examples from the logs

4. **Create a visual flow diagram** in markdown showing the sequence

## Status
- ✅ Step 1: Created `references/hooks-and-events-payloads.md` (903 lines) - comprehensive payload reference
- ✅ Step 2: Updated `references/runtime-sequence.md` (124 lines) - clear hooks vs events distinction with jq commands
- ✅ Step 3: Updated `SKILL.md` (316 lines) - improved lifecycle analysis, hooks vs events section
- ✅ Step 4: Final review complete

## Summary of Improvements

1. **New file: `hooks-and-events-payloads.md`**
   - Complete runtime flow in 9 stages
   - 14 hooks documented with exact input/output shapes and mutability
   - 7 event types documented with payload shapes
   - 6 practical mutation examples in TypeScript
   - Quick reference table for hook/event name collisions

2. **Updated `runtime-sequence.md`**
   - Added "Hooks vs Events" section with comparison table
   - Tagged timeline with 🔧/📡 symbols
   - Added jq commands to distinguish hooks from events in logs
   - Added "Tool Part State Lifecycle" section
   - Updated "Common Mistakes" to include hook/event confusion

3. **Updated `SKILL.md`**
   - Rewrote `<runtime-lifecycle-analysis>` with 🔧/📡 notation and mutation notes
   - Added "Hooks vs Events: How to Tell Them Apart" subsection
   - Added reference to new payload documentation
   - Updated references list to include all three reference files

## Key Insight Documented
The critical discovery from analyzing the two JSONL files:
- `with-events.jsonl` had the `event` hook enabled, so we see BOTH hooks (top-level types) AND events (nested in `type: "event"`)
- `no-events.jsonl` had the `event` hook disabled, so we only see hooks
- Some names like `tool.execute.before` exist as BOTH a hook AND an event type
- Hooks receive `(input, output)` and can mutate `output`; events are read-only notifications
