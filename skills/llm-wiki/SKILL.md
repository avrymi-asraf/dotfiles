---
name: llm-wiki
description: Build and maintain a personal LLM-powered knowledge base using Karpathy's LLM Wiki pattern. Use when the user wants to create a compounding knowledge base from documents, build an LLM wiki, manage research notes with AI, mentions "llm wiki", "karpathy wiki", or wants a persistent knowledge base alternative to RAG.
---

<llm-wiki>
Implements Andrej Karpathy's LLM Wiki pattern — a persistent, compounding knowledge base built and maintained by an LLM from raw source documents (papers, articles, notes). Instead of re-reading raw files on every query (RAG), the LLM pre-compiles knowledge into structured, interlinked markdown pages that accumulate over time.

### Topics Covered
- **[Architecture]** — three-layer structure: raw sources → wiki pages → schema
- **[Folder-Setup]** — directory layout and CLAUDE.md schema file
- **[Entity-Pages]** — format and rules for wiki pages with `[[wiki-links]]`
- **[Core-Operations]** — the three operations: Ingest, Query, Lint (with ready-to-use prompts)
- **[vs-RAG]** — when to use LLM Wiki vs RAG
- **[Common-Mistakes]** — pitfalls to avoid
- **[examples]** — end-to-end walkthrough

</llm-wiki>

<Architecture>
Three layers:

1. **Raw Sources** — immutable originals (PDFs, articles, notes) in `raw/` — never modified
2. **Wiki** — LLM-generated markdown entity pages in `wiki/` — the compounding artifact
3. **Schema** — `INDEX.md` at the wiki root, defining page structure and operation workflows

Two special navigation files live inside `wiki/`:
- `index.md` — category-organized catalog of all pages
- `log.md` — append-only chronological record; prefix each entry: `[INGEST]`, `[QUERY]`, `[LINT]`

</Architecture>

<Folder-Setup>
```
my-wiki/
├── raw/          # source documents (PDFs, txt, md) — never edit these
├── wiki/         # compiled entity pages — LLM writes here
│   ├── index.md  # page catalog by category
│   └── log.md    # operation history
└── INDEX.md     # schema: page structure, operation rules
```

Always launch Claude Code from the `my-wiki/` root so it can access both `raw/` and `wiki/`.

**Minimal INDEX.md:**
```markdown
# Wiki Schema
- One concept per page, Wikipedia style
- Use [[wiki-links]] for cross-references
- Flag contradictions: `> ⚠️ Contradicts [[Page]] on X`
- Filenames: kebab-case matching the concept name
- Always update index.md and append to log.md after any operation
```

</Folder-Setup>

<Entity-Pages>
Each page covers **one concept or entity**:

```markdown
# Concept Name

## Summary
One-paragraph overview.

## Details
...

## Related
- [[Related Concept A]]
- [[Related Concept B]]

## Sources
- raw/paper1.pdf (section 3)
```

Rules:
- One concept per file — split if a page exceeds ~300 lines
- `[[wiki-links]]` for cross-references (Obsidian-compatible, enables graph view)
- Contradictions flagged inline: `> ⚠️ Contradicts [[Other Page]] on X`
- Filename = kebab-case concept name: `attention-mechanism.md`

</Entity-Pages>

<Core-Operations>

### Ingest — add new source documents
```
Read all files in raw/ not yet recorded in log.md.
For each, extract key concepts and update 10-15 wiki pages in wiki/.
Create new pages or update existing ones. Use [[wiki-links]].
Flag contradictions with existing pages inline.
Update index.md and append [INGEST] entries to log.md.
```

### Query — ask a question, persist the answer
```
Answer: <your question>
Use only wiki/ pages as source.
If the answer is useful and non-trivial, save it as a new wiki page.
Update index.md and append a [QUERY] entry to log.md.
```

### Lint — periodic health check (every ~20 new pages)
```
Audit wiki/ for:
- Contradictions between pages
- Orphaned pages (no incoming [[links]])
- Stale claims conflicting with newer pages
- Missing cross-references between related concepts
Fix issues in place. Append a [LINT] entry to log.md.
```

</Core-Operations>

<vs-RAG>

| | RAG | LLM Wiki |
|---|---|---|
| Persistence | Stateless, per-query | Permanent, compounding |
| Synthesis | Re-generated every time | Pre-compiled once |
| Contradictions | Not detected | Flagged at ingest |
| Best for | Large dynamic corpora | Deep research on a focused domain |

**Use LLM Wiki when:** focused topic, documents accumulate over time, you want synthesized insight not just retrieval.

**Use RAG when:** broad or frequently-changing corpus, exact source citations are required.

</vs-RAG>

<Common-Mistakes>

- **Overloading pages** — one concept per file; split long pages
- **Skipping lint** — contradictions accumulate silently; run every ~20 pages
- **Mixing unrelated topics** — focused wikis produce richer link graphs and better synthesis
- **Ignoring log.md** — always append after every operation; it's the audit trail
- **Wrong working directory** — launch Claude Code from `my-wiki/` root, not from `wiki/`

</Common-Mistakes>

<examples>
Building a wiki on transformer architectures from 5 papers:

1. Create structure: `my-wiki/raw/` and `my-wiki/wiki/` with empty `index.md` and `log.md`
2. Drop papers into `raw/`: `attention-all-you-need.pdf`, `bert.pdf`, `gpt3.pdf`, `rlhf.pdf`, `foundation-models.pdf`
3. Launch `claude` from `my-wiki/`, run the Ingest prompt
4. Claude creates: `attention-mechanism.md`, `positional-encoding.md`, `masked-language-modeling.md`, `rlhf.md`...
5. Each page has `[[wiki-links]]` → open `wiki/` as Obsidian vault → Ctrl+G shows concept network
6. Query: "What's the difference between encoder-only and decoder-only transformers?" → saved as `encoder-vs-decoder.md`
7. After 20 pages, run Lint → Claude flags `bert.md` and `roberta.md` make conflicting claims about pretraining data size → fixes in place

**Common mistake caught:** user opened Obsidian on `my-wiki/` instead of `my-wiki/wiki/` — graph view shows raw PDFs mixed with pages. Fix: open only the `wiki/` subfolder as the Obsidian vault.

</examples>
