---
name: skills
description: Manage, update and create Agent Skills (SKILL.md files). MUST be read before editing any SKILL.md file. Use when the user asks to update, modify, fix, create, improve, or review any skill — even if they point directly to the skill file path.
---
# Managing Agent Skills

**STOP — Read this skill before editing any SKILL.md.** Even if the user gives you the file path directly, do NOT just open and edit it. Follow the workflow in this skill to maintain quality and consistency.

Skills are markdown files that teach agents how to perform specific tasks. This skill guides you through creating and updating them.

## Understanding the Skill

Before making changes, make sure you understand:

1. **Purpose and scope**: What tasks does this skill help with?
2. **Key domain knowledge**: What domain knowledge is required?
3. **Trigger scenarios**: When should the agent automatically apply this skill?
4. **Target location**: Personal (`~/.cursor/skills/`) or project (`.cursor/skills/`)?

If unsure, verify with the user. Use AskQuestion when available.

---

## Skill File Structure

### Directory Layout

```
skill-name/
├── SKILL.md              # Required - main instructions
├── reference.md          # Optional - detailed documentation
├── examples.md           # Optional - usage examples
└── scripts/              # Optional - utility scripts
```

### Storage Locations

| Type | Path | Scope |
|------|------|-------|
| Personal | ~/.cursor/skills/skill-name/ | Available across all your projects |
| Project | .cursor/skills/skill-name/ | Shared with anyone using the repository |

**IMPORTANT**: Never create skills in `~/.cursor/skills-cursor/` — reserved for Cursor internals.

### SKILL.md Structure

Every skill requires a `SKILL.md` with YAML frontmatter and markdown body:

```markdown
---
name: your-skill-name
description: Brief description of what this skill does and when to use it
---

# Your Skill Name
A brief introduction about the system this skill covers.

## <tool or workflow section>

## Examples
Concrete examples of using this skill's tools and workflows.
```

### Required Metadata

| Field | Requirements | Purpose |
|-------|--------------|---------|
| `name` | Max 64 chars, lowercase letters/numbers/hyphens | Unique identifier |
| `description` | Max 1024 chars, non-empty | Helps agent decide when to apply the skill |

Use [Common Patterns](Common Patterns.md) for writing patterns.

---

## Writing Effective Descriptions

The description is **critical** — the agent uses it to decide when to apply the skill.

1. **Write in third person** (injected into system prompt):
   - Good: "Processes Excel files and generates reports"
   - Bad: "I can help you process Excel files"

2. **Be specific and include trigger terms**:
   - Good: "Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction."
   - Bad: "Helps with documents"

3. **Include both WHAT and WHEN**:
   - WHAT: What the skill does (specific capabilities)
   - WHEN: When the agent should use it (trigger scenarios)

---

## Core Authoring Principles

### 1. Concise is Key

The context window is shared. Every token competes for space. The agent is already smart — only add context it doesn't have.

### 2. Progressive Disclosure

**SKILL.md must be under 300 lines.** Put essentials in SKILL.md; detailed reference in separate files read on demand. Keep references one level deep.

### 3. Set Appropriate Degrees of Freedom

| Freedom Level | When to Use | Example |
|---------------|-------------|---------|
| **High** (text) | Multiple valid approaches | Code review guidelines |
| **Medium** (templates) | Preferred pattern with variation | Report generation |
| **Low** (specific scripts) | Fragile, consistency critical | Database migrations |

### 4. Be a Modular Tool Set

The skill should be a modular tool set. The agent must understand the big picture and know how to use the tools. Think about simple, clear MCP tools that perform the tasks.

MCP tools are preferred over generated code — more reliable, save tokens, ensure consistency.
Use the skill mcp to build the tools.

---

## Anti-Patterns

- **Windows paths**: Use `scripts/helper.py`, not `scripts\helper.py`
- **Too many options**: Provide one default approach, mention alternatives only when clearly needed
- **Time-sensitive info**: Use "Current method" / "Old patterns (deprecated)" sections
- **Inconsistent terminology**: Pick one term and use it throughout
- **Vague names**: Use `processing-pdfs`, not `helper` or `utils`

---

## Creating a New Skill

1. **Discovery**: Gather purpose, location, triggers, constraints, existing patterns
2. **Design**: Draft name, write description (with WHAT + WHEN), outline sections, identify supporting files
3. **Implement**: Create directory, write SKILL.md with frontmatter, create supporting files
4. **Verify**: Run the checklist below

---

## Updating an Existing Skill

When updating, the most important thing is **keeping consistency and quality**.

1. **Read the full skill first** — understand its structure, style, and voice
2. **Identify the root cause** — don't pile on fixes and warnings. Determine what's fundamentally wrong and fix that
3. **Integrate changes naturally** — new content must match the existing style and flow. Do NOT add a separate "rules" or "warnings" section
4. **Stay under 300 lines** — if adding content, trim elsewhere
5. **Verify**: Run the checklist below

---

## Summary Checklist

### Core Quality
- [ ] Description is specific and includes trigger terms (both WHAT and WHEN)
- [ ] Written in third person
- [ ] SKILL.md is under 300 lines
- [ ] Consistent terminology throughout
- [ ] Examples are concrete, not abstract

### Structure
- [ ] File references are one level deep
- [ ] Progressive disclosure used appropriately
- [ ] Workflows have clear steps

### Update-Specific
- [ ] Read the full existing skill before editing
- [ ] Changes match existing style and voice
- [ ] No "pile of fixes" — root cause addressed
- [ ] New content integrated into existing sections
