---
name: code-as-tools
description: How to write code for research, experimentation, and exploration — as a small set of composable, notebook-usable, well-documented tools rather than a fixed pipeline. Use this whenever the user is writing analysis, experiment, research, or exploratory code (Jupyter notebooks, data probing, model evaluation, ablations, one-off investigations), or asks you to refactor, review, or extend such code. Apply it even when the user only asks for "a script" — if the goal is to find something out rather than to run one fixed job, this skill applies.
---

# Code as Tools

## When this applies

Two kinds of code exist. **Product code** runs one known path correctly and repeatedly.
**Research code** exists to answer questions that are not yet known. This skill is about the second kind.

The signal: the user does not yet know what they will run, in what order, or how many times.
If you cannot state the single correct execution path, write tools — not a pipeline.

## The rules

**1. Each function is a tool.**
A tool does one meaningful thing, takes explicit inputs, returns a usable value.
No hidden global state, no side effects the caller cannot see, no function that only makes
sense as step 4 of one particular script.

**2. Design the toolset first. This is the real work.**
Before writing bodies, decide what the tools are and where the seams between them go.
Ask: what are the units the user will want to recombine? Those are the tools.
A bad seam costs more than a bad implementation — implementations get rewritten, seams get built on.

**3. Versatile, but few.**
Each tool should serve many needs and many callers: parameterize the axes that will actually vary,
and prefer one tool with a clear parameter over three near-duplicate tools.
But the set stays small and modular. A large toolset is a failure, not thoroughness —
if the user cannot hold the whole set in their head, they will not use it.
Before adding a tool, try to compose it from existing ones.

**4. Documentation is load-bearing, not decoration.**
Because the execution path is unknown, the docs are how the next person (or agent) discovers
what is possible. For every tool state: what it does, what each parameter means and its units,
what it returns, and — most important — **when you would reach for it**.
Also record what it does *not* handle, and any assumption that would silently produce wrong results.
Write for a reader who has never seen the code and is scanning to find a tool that fits.

**5. Make the composition visible.**
Any concrete experiment is a short, readable script that calls the tools in sequence.
Keep that layer thin: if logic accumulates in the script, it belongs in a tool.
The script should read like the description of the experiment.

**6. The notebook is the field of experimentation — design for it.**
Tools are tried and tested in Jupyter, not only behind a CLI. Every tool must be usable
*as-is* from a notebook cell, with no wrapper and no entry-point ceremony. Concretely:

- Import and call directly — no `argparse`, no `if __name__ == "__main__"` gate around the real logic.
- Return objects, not printed text or exit codes. The caller inspects the return value in the next cell.
- No `sys.exit()`, no process-level side effects, no swallowing exceptions — a traceback in a cell is useful.
- Configuration arrives as arguments, not as env vars or a config file read at import time.
- Keep single calls interruptible and cheap enough to iterate on; expose the granularity that lets
  the user run one piece, look at it, and continue.
- If a CLI is wanted, it is a thin shell over the same tools — never the only way in.

**7. Stage-by-Stage Visualization.**
In research and data exploration, qualitative visual inspection is as critical as quantitative metrics.
- For every core stage (data generation, pruning/filtering decisions, training progress, model evaluation), provide dedicated visualization helpers.
- Visualizers should accept the exact structured objects returned by the tools (e.g. `render_diff(trace, decision)`, `render_comparison(base, pruned)`).
- Make visual output directly renderable inside notebook cells (`IPython.display.HTML`), in the terminal (via Rich/ANSI), and optionally via lightweight interactive viewers (Gradio/Streamlit) for deep inspection.

## The design-time check

Before writing code, and again before adding to an existing set, ask explicitly:

1. Is this a set of tools, or is it ordinary single-path code? (Which does the task actually call for?)
2. Does this new piece fit logically into the existing set — or does the set need to change to accommodate it?
3. Can it really be used properly in a notebook, as it stands?

If (2) says the set needs to change, say so rather than bolting the new piece on.
If (3) fails, the design is wrong — fix it before implementing.

## Applying it

- **Writing new code** — propose the toolset (names + one-line purpose each) before implementing.
- **Reviewing code** — flag functions that only work in one order, near-duplicate tools that should
  be one parameterized tool, tool sprawl, and undocumented assumptions.
- **Extending code** — first ask whether an existing tool should be widened. Add a new tool only
  if it is a genuinely new unit of work.

## Anti-patterns

| Smell | Fix |
| --- | --- |
| `run_everything()` that does all the steps | Split at the points where the user would want to look at intermediate results |
| Functions that must be called in a fixed order | Pass state explicitly; make each callable alone |
| `analyze_v2`, `analyze_new`, `analyze_final` | One tool, one parameter |
| A docstring restating the function name | Say when to use it and what it assumes |
| Configuration flags accumulating on one tool | The seam is wrong — split it |
| Logic reachable only through the CLI entry point | Put it in a tool; the CLI just calls it |
| Tool prints results instead of returning them | Return the object; let the caller print |
| Reads env vars or config files at import time | Take it as an argument |