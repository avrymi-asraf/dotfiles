# dotfiles — Workspace Instructions

This repository is a personal collection of AI coding-agent configurations: VS Code settings, Copilot/Cursor rules, slash-command prompts, chat modes, and keybindings. There is no runtime application — the "output" is config files that get copied into other projects or synced into VS Code.

---

## Repository Structure

```
chatmode/       # VS Code Copilot chat mode definitions (.chatmode.md)
commands/       # Reusable slash-command / prompt files (.md)
prompts/        # Agent prompt files (.prompt.md)
rules/          # Cursor-style rules (.mdc) applied to specific file types or always
vsc/            # VS Code settings and keybindings JSON files
```

### File types

| Extension | Purpose |
|-----------|---------|
| `.chatmode.md` | Copilot Chat mode — declares available tools and a system prompt |
| `.prompt.md` | Agent prompt — invoked explicitly via `/command` or attach |
| `.mdc` | Cursor rule — `globs`/`alwaysApply` frontmatter controls when it fires |
| `.md` (commands/) | Slash-command prompt text, usually referenced by Copilot or Cursor |
| `.json` (vsc/) | VS Code `settings.json` / `keybindings.json` fragments |

---

## Conventions

### Issue / ticket descriptions (GitLab, GitHub, Jira)
All generated issues and tickets **must** follow this three-section structure — keep each section short and purposeful, no low-level implementation details:

1. **Current State** — describe the existing problem or situation.
2. **Desired Change (What & Why)** — what must change and the core rationale.
3. **High-Level Plan (How)** — 2-3 architectural steps or alternative directions; pseudo-code or diagrams are allowed.

### Jira-specific
- Project key is always **REMCLOUD**.
- Always add the source repository name as a label.

### MCP tool usage for GitLab issues
1. `list_projects` with `{"search": "<repo-name>"}` to get the `project_id`.
2. `create_issue` with the three-section description.

### Commit messages
Terse imperative, 2–5 words, no punctuation, action verb first (e.g. `Add user auth`, `Fix login bug`). Output only the message — nothing else.

### Frontend (single-file HTML)
- All code in one `index.html`; no external file references except CDNs.
- Vanilla JS (ES6+), Semantic HTML5, optional Tailwind via CDN.
- Top of file: comment block with Architecture, Component Map, and Configuration guide.
- Style: minimalist, high-contrast (white/light-gray + bold accent colour).

### Logging
Format every log line as: `<time> <stage> : <most-indicative data from this stage>`

### Scripts
- Single central script; helpers only when they aid readability.
- Clarity over cleverness; prefer the simplest working library.

### General code rules
- Understand the full system before writing a line — list files, detect patterns.
- Challenge vague requirements; identify inputs, outputs, constraints.
- Max **1600 lines per file** — flag files approaching this limit.
- No unnecessary try-catch, no side effects without calling them out.
- Format on save; use linters where available.

### README / documentation
- The README is the entry point for both humans and agents — a gateway, not an implementation manual.
- Structure: Goal → Structure / Program Flow → File Structure → Usage.
- Do **not** create new documentation files unless explicitly asked.
- Update `README.md` in-place; never restructure without a reason.

---

## Adding new dotfiles

1. Place the file in the correct directory (see table above).
2. For rules (`.mdc`), set `globs` and/or `alwaysApply` in the YAML frontmatter.
3. For chat modes, declare only the tools that are actually needed.
4. Keep prompts focused — one command, one responsibility.
5. Update `README.md` if the new file changes the visible surface of the repo.
