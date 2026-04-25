---
name: gemini-deep-research
description: Local MCP server for Google Gemini Deep Research interactions using explicit regular/max start tools, explicit file-capable variants, and status polling. Use when the user wants long-running Deep Research jobs with explicit start + poll control.
---

# Gemini Deep Research MCP

This skill provides a local MCP server for Google Gemini Deep Research interactions.

## Files

- `skills/gemini-deep-research/mcp-server.py`

## Requirements

- `GOOGLE_API_KEY` must be set in the environment.
- Optional: `GEMINI_API_BASE_URL` to override the default API base (`https://generativelanguage.googleapis.com/v1alpha`).

## Run Manually

```bash
uv run skills/gemini-deep-research/mcp-server.py
```

## Tools Exposed

- `deep_research_start_regular(prompt, additional_instructions=None, file_search_stores=None)`
- `deep_research_start_max(prompt, additional_instructions=None, file_search_stores=None)`
- `deep_research_start_regular_with_files(prompt, file_uris, additional_instructions=None, file_search_stores=None)`
- `deep_research_start_max_with_files(prompt, file_uris, additional_instructions=None, file_search_stores=None)`
- `deep_research_start_file_aware(prompt, file_uris, mode="regular", additional_instructions=None, file_search_stores=None)`
- `deep_research_poll(interaction_id)`

## Usage Pattern

1. Call one start tool and capture `interaction_id`.
2. Poll with `deep_research_poll` until `done` is `true`.
3. Read the `raw` field for final model output.

## Notes

- Input validation returns explicit `Error: ...` messages.
- Regular mode defaults to `deep-research-preview-04-2026`; max mode defaults to `deep-research-max-preview-04-2026`.
- Start requests use Deep Research `agent`, set `background=true`, and send `agent_config.type="deep-research"`.
- Tools are sent using typed entries and include `file_search.file_search_store_names` when `file_search_stores` is provided.
- File-aware requests require `file_uris` as URI-like strings.
- This server intentionally keeps scope minimal: start interaction + poll status.
