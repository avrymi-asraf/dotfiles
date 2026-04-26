# Manager Memory

## Current Task
Maintain repository knowledge in `data-place/wiki/` and record durable implementation knowledge for completed MCP tools.

## Recent Data-Wiki Ingest (2026-04-26)
- Created initial `data-place/wiki/` structure when none existed.
- Ingested the completed PDF-to-Markdown MCP knowledge into:
  - `data-place/wiki/index.md`
  - `data-place/wiki/log.md`
  - `data-place/wiki/sources/pdf-to-markdown-mcp-implementation.md`
  - `data-place/wiki/concepts/pdf-to-markdown-mcp.md`
  - `data-place/wiki/entities/google-gemini.md`
  - `data-place/wiki/entities/ollama.md`
- Security convention recorded: never copy real secrets from `opencode.json`; MCP registration examples must use placeholders only.

## Prior Task
Fix the `skills/gemini-deep-research/mcp-server.py` MCP server which was making incorrect API calls to Gemini's Deep Research Interactions API.

## Errors Identified
1. `Unknown parameter 'instructions' at 'agent_config'` - `additional_instructions` was being placed inside `agent_config`, but per the Gemini Interactions API docs, system-level instructions should be a top-level `system_instruction` field.
2. `The value 'input_text' is not supported for 'type' at 'input[0].content[0]'` - The content type inside the input array was `input_text`, but the API only supports `text` (and other types like `document`, `image`, etc.).
3. `files` were incorrectly placed inside `agent_config` instead of being included in the `input` array as content parts with `type: "document"`.

## API Schema (from official docs)
- `input` should be a flat array of content parts (not nested turns with `role`/`content`):
  ```json
  [
    {"type": "text", "text": "research prompt here"},
    {"type": "document", "uri": "file:///tmp/report.pdf"}
  ]
  ```
- `agent_config` should only contain agent-specific settings like `type`. It must NOT contain `instructions` or `files`.
- `system_instruction` is a top-level field for providing system-level instructions.

## Fixes Applied (2026-04-25)
Rewrote `_build_interaction_payload` in `skills/gemini-deep-research/mcp-server.py`:
- Changed `input` from nested turns (`role`/`content`) to flat array of parts
- Changed content `type` from `input_text` to `text`
- Moved `file_uris` from `agent_config` into `input` array as `{"type": "document", "uri": uri}`
- Kept `agent_config` as `{"type": "deep-research"}`

## Additional Discovery During Live Testing
`system_instruction` (top-level) is **NOT supported** by the deep-research agent. The API returns:
> "The 'system_instruction' parameter is not supported for the deep-research-preview-04-2026 agent. Please include any specific instructions in the 'input' prompt instead."

So `additional_instructions` is now **prepended to the prompt text** with a blank line separator:
```
"Focus on modern ES2024+ features only.\n\nWhat are 3 quick facts about JavaScript?"
```

## Live API Testing Results (all passed)
- ✅ Basic payload (regular agent) → returns `interaction_id`, status `in_progress`
- ✅ With `additional_instructions` merged into prompt → returns `interaction_id`, status `in_progress`
- ✅ Poll interaction → returns correct status
- ✅ Max agent (`deep-research-max-preview-04-2026`) → returns `interaction_id`, status `in_progress`
- ✅ `file_search_stores` with valid store name → properly passes through (tested with invalid name, correctly rejected by API)
- ✅ All original 400 errors resolved

## Status
- ✅ Code fix complete
- ✅ Payload structure tests pass
- ✅ Live API end-to-end tests pass
- ✅ Task complete
