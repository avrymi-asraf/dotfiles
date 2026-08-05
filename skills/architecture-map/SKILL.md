---
name: architecture-map
description: Generate a production-quality interactive self-contained HTML architecture diagram plus agent-ready JSON from any codebase. Use when the user asks for architecture visualization, repo architecture, interactive architecture map, system diagram, codebase structure, architecture HTML, flow diagram of the app, nodes and edges map, or to explain how the system is structured with selectable flows.
---

# Architecture Map

Produce two complete, ready-to-use deliverables that make any codebase self-explaining:

1. **architecture.html** — single self-contained interactive visualization
2. **architecture.json** — structured graph for other AI agents

The HTML must match the quality of professional architecture explorers (layered groups, path highlighting on flow selection, rich tooltips, clean dark or light professional UI). The JSON must be immediately consumable by agents without further parsing.

## When to Activate

Trigger on any request that involves understanding, visualizing, or documenting the high-level structure and critical flows of a repository or application. Prefer this skill over ad-hoc diagrams or Mermaid when the user wants something interactive and durable.

## Core Workflow (mandatory)

### 1. Deep repository reconnaissance

Do not stop at directory listings. Use tools aggressively:

- Map top-level structure, package manifests, entry points, configs, Dockerfiles, CI, infra-as-code.
- Identify major modules, services, layers, data stores, external integrations, and client surfaces.
- Read the most important source files (main, routers, services, models, clients, workers) to extract real call/data relationships — do not invent edges.
- Prefer evidence from code + docs over pure inference. Record file paths that justify each node and edge.

If the working directory is not the repo root, ask or locate the correct root. Support monorepos by focusing on the relevant package or producing a system-level map.

### 2. Model the architecture

Define:

- **Nodes** — meaningful components at the right level of abstraction (prefer services/modules over individual functions unless the function is a critical boundary). Group them into logical layers or swimlanes (Client Surfaces, API Gateway, Auth, Core Services, Data, Background Workers, External Services, etc.).
- **Edges** — directed relationships with clear labels (calls, reads, writes, publishes, authenticates, deploys, etc.). Only include edges that actually exist in the system.
- **Flows** — 5–12 of the most important end-to-end paths (user journeys, request lifecycles, build/deploy pipelines, auth sequences, data pipelines, webhook handlers). Each flow must have ordered steps that map to real nodes and describe what happens and what data moves.

Aim for clarity over completeness. A diagram with 15–40 well-chosen nodes is almost always better than 200.

### 3. Emit the two artifacts

Write both files to the current working directory (or `/home/workdir/artifacts/` if that is more appropriate). Name them `architecture.html` and `architecture.json` unless the user specifies otherwise.

After writing, briefly summarize the key layers, the most critical flows, and any surprising architectural observations.

## JSON Schema (exact)

```json
{
  "meta": {
    "title": "string — short project name + Architecture",
    "description": "string — one-paragraph overview of the system",
    "generated_at": "ISO-8601",
    "repo_root": "string — relative or absolute path analyzed"
  },
  "nodes": [
    {
      "id": "kebab-case-unique",
      "label": "Human readable name",
      "type": "client|frontend|api|service|function|worker|database|storage|queue|external|infra|auth|other",
      "group": "Layer or swimlane name",
      "description": "What this component does and why it exists",
      "files": ["relative/path/to/key/file.ts", "..."],
      "tech": ["optional list of frameworks or languages"]
    }
  ],
  "edges": [
    {
      "id": "optional-unique",
      "source": "node-id",
      "target": "node-id",
      "label": "calls|reads|writes|triggers|authenticates|publishes|depends-on|...",
      "description": "Short explanation of the relationship"
    }
  ],
  "flows": [
    {
      "id": "kebab-case",
      "name": "Short flow name",
      "description": "What this flow accomplishes",
      "steps": [
        {
          "order": 1,
          "node": "node-id",
          "action": "Concise action title",
          "details": "What happens, key data exchanged, important side effects"
        }
      ]
    }
  ]
}
```

Validate the JSON mentally before writing: every flow step must reference an existing node id; every edge source/target must exist.

## HTML Requirements (non-negotiable quality bar)

Produce a **single self-contained HTML file**. No external build step. Use a CDN for the graph library (vis-network is recommended; cytoscape.js is also acceptable).

### Visual & interaction design

- Dark professional theme by default (near-black background, subtle borders, high-contrast text). Support a clean light alternative if the user prefers.
- Left/main area: interactive force-directed or hierarchical graph of nodes + edges.
- Right panel (≈320–380 px): 
  - List of all flows (clickable)
  - When a flow is selected, show its ordered STEPS below with numbers and details
  - Clear selection button
- Selecting a flow must:
  - Highlight the exact path (nodes + edges) in a strong accent color (e.g. yellow/gold)
  - Dim or de-emphasize unrelated nodes/edges
  - Populate the steps panel
- Hover tooltips on every node showing label, type, description, and key files.
- Legend for node types / groups (color coding).
- Title + short description at the top.
- Responsive: usable on laptop and wide desktop. On narrow screens the right panel can collapse or stack.
- Smooth interactions, no jank. Nodes should be readable (avoid extreme overlap).

### Implementation guidance

- Embed the full graph data (nodes, edges, flows) as a JavaScript constant inside the HTML so the file is truly portable.
- Use distinct colors per `group` or `type`.
- Give nodes of different types distinct shapes or border styles if helpful.
- Include a small header with project name and generation note.
- Keep the total HTML under ~150–200 KB when possible (data dominates).

You may start from the template in `assets/architecture-template.html` and replace the data section, or generate a complete file from scratch. The visual result must feel polished and intentional.

## Quality checklist before delivery

- [ ] Every major architectural concern is represented
- [ ] Flows are real end-to-end paths, not toy examples
- [ ] JSON is valid and complete
- [ ] HTML opens in any modern browser with no console errors
- [ ] Path highlighting works correctly for every flow
- [ ] Tooltips and legend are present
- [ ] No invented components or relationships

## Optional extras (when useful)

- Export a short `ARCHITECTURE.md` summary that points to the two files and lists the top flows.
- If the user already has Graphify installed, you may offer to run it as a complementary deterministic AST pass, then enrich or reconcile with the richer flow-centric view produced by this skill.
- For very large monorepos, produce a system-level map first, then offer deeper maps of individual packages.

## Anti-patterns

- Do not produce a static image or pure Mermaid when interactive HTML was requested.
- Do not dump every file as a node.
- Do not create flows that cannot be traced through actual code.
- Do not leave the HTML dependent on local files or unpkg that may break offline.

The goal is that after receiving these two files the user (or another agent) can understand the system architecture and its critical paths without reading the source.