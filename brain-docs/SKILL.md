---
name: brain-docs
description: >-
  Set up and maintain a "project brain" — a brain/ folder holding three living
  documents (decisions.md, flow.md, todo.md) that give a project persistent
  memory across chat sessions. Use this skill whenever the user wants a
  decision log, architecture/flow notes, project memory, living documentation,
  or notes that survive between sessions ("set up a project brain", "start a
  decision log for this repo", "remember why we chose X"). Also use it in any
  repo that already has a brain/ folder: after completing a meaningful code
  change, when the user says "update the brain docs" or "log this decision",
  when a risk/limitation/idea surfaces worth writing down, or when the user
  asks why a past decision was made (read decisions.md before answering).
---

# brain-docs — a living project memory

Chat sessions end; the reasoning behind code shouldn't. This skill maintains a
`brain/` folder of three documents that together act as the project's memory:

| File | Holds | Answers |
|---|---|---|
| `brain/decisions.md` | Dated decision log (newest first) | "Why is it built this way?" |
| `brain/flow.md` | Whole-system execution flow | "What calls what, in what order?" |
| `brain/todo.md` | Tagged action items, caveats, ideas | "What's known-broken, known-limited, or worth doing?" |

The system only works if the docs are updated **incrementally, as you work** —
not in a batch when someone remembers to ask. A future session (or a future
maintainer) relies on them being current.

There are two modes. Check whether `brain/` exists in the project root:
- **No `brain/` folder, or the user asks to set one up → Setup mode.**
- **`brain/` exists → Maintain mode.**

---

## Setup mode

1. **Create `brain/`** in the project root and seed the three files from
   `assets/templates/` (in this skill's folder). Adapt each file's title line
   to the project's name; keep the maintenance blockquotes — they remind
   future sessions of the rules even if this skill doesn't load.

2. **Ask whether `brain/` should be git-ignored.** Don't assume — this is a
   real tradeoff the user owns:
   - *Git-ignored (local)*: the notes can be candid — honest tradeoffs,
     "this is a hack", API-billing gripes — because nobody else reads them.
     But they live on one machine and won't reach teammates or CI.
   - *Committed*: the whole team (and every future clone) shares the memory,
     at the cost of writing for an audience.
   Apply their choice (add `brain/` to `.gitignore`, or not).

3. **Install the standing rule into the project's `CLAUDE.md`** (create the
   file if it doesn't exist) by inserting the block from
   `assets/claude-md-snippet.md`. This step is what makes the system work:
   `CLAUDE.md` is loaded every session unconditionally, while a skill only
   loads when triggered — so the always-on update discipline must live there.
   If a `CLAUDE.md` exists, add the block near the top and adapt its wording
   to sit naturally in the file; don't duplicate it if a version is already
   present.

4. **Seed `flow.md` with a real trace.** Explore the codebase and write the
   actual entry points, call paths, and key files into the template's
   sections — a skeleton with placeholders has no value until it describes
   the real system. If the codebase is large, trace the primary execution
   path end-to-end first and note which areas remain unmapped. Only skip
   this (leaving the template + a 🔴 todo item to do it later) if the user
   asks to skip it.

5. `decisions.md` starts empty of entries (the first real decision will
   arrive soon enough). If the setup itself involved choices worth recording
   — e.g. the user picked committed-vs-ignored for a specific reason — that
   can be the first entry.

For the precise shape of each file, see the templates; for what good entries
look like, read `references/examples.md`.

---

## Maintain mode

Update the docs **before ending any turn** in which you changed code, made a
decision, or learned something worth keeping. Match each file's existing
structure and tone. If one of the three files is missing, recreate it from
its template.

### `brain/decisions.md` — the decision log

Append an entry under a dated heading (`## YYYY-MM-DD — <short title>`),
**newest first**, for every *meaningful* decision: library/pattern/tradeoff
choices, why an alternative was rejected, mid-implementation reversals.
Skip trivial mechanical edits. The test: would a future maintainer ever ask
"why is it like this?" — if yes, log it.

Use the **D / W / A / T** format:

- **D:** the decision — what was done, with the key files/seams named.
- **W:** why — the need or problem that drove it.
- **A:** alternative(s) rejected — and *why* they lost. This is the most
  valuable line: it stops future sessions from relitigating settled choices.
- **T:** tradeoff accepted — what got worse, and why that's acceptable.

A line like **Verified:** (how the change was proven to work) is a welcome
optional fifth part. Several related sub-decisions from one piece of work can
share a dated section as numbered sub-entries.

### `brain/flow.md` — whole-system execution flow

When a change alters *how execution travels* — a new endpoint, a new call in
a path, changed inputs/outputs of a stage, a new provider/adapter, a new
frontend data path — update:

1. the relevant **call-tree section** (indented tree of
   `file :: function → what it calls`, annotated with what each hop does),
2. the **Key files** table, and
3. the **end-to-end trace** at the bottom, if the main path changed.

Tag every edited spot inline with `[CHANGED: <area>]`, where `<area>` is a
short slug for the piece of work (e.g. `[CHANGED: auth]`). The tags let a
reader diff the system's evolution at a glance; rationale for the change
belongs in `decisions.md`, not here. Keep the document **whole-system, not
session-scoped**: it describes how the entire codebase executes today, with
recent edits tagged — it is not a changelog. If you add or rename a module or
function that appears in the doc, fix its node.

### `brain/todo.md` — action items, caveats, ideas

- **Add** anything that surfaces while working: correctness or security
  risks noticed while reading (even in code you weren't asked to touch),
  by-design limitations worth remembering, feature ideas, tech debt.
- **Check off** (`[x]`) items completed, and **remove or strike** items that
  no longer apply — a stale todo list stops being trusted.
- Every item carries a severity tag and, where possible, a `file:line` ref:

  - 🔴 **action required** — blocks something; must be done (deploy steps,
    migrations, missing config).
  - 🟠 **correctness / security** — observed risk; verify and fix.
  - 🟡 **known limitation** — by design; remember it, don't "fix" it blindly.
  - 🟢 **feature** — improvement idea.
  - 🔵 **tech debt** — cleanup that can wait.

- Mark provenance when useful: `(session)` for items surfaced while working
  vs. items imported from a roadmap or handoff doc.

### The cross-file rule

One piece of work often touches all three: if a task fixes a caveat listed in
`todo.md` **and** embodies a decision, then check it off in `todo.md`, log
the reasoning in `decisions.md`, and re-trace the affected path in `flow.md`.
Ask "which of the three does this change concern?" every time — the honest
answer is frequently "more than one".

---

## Answering from the brain

When the user asks "why did we do X?", "how does Y work?", or "what's still
open?" in a project with a `brain/` folder, read the relevant doc
(`decisions.md` / `flow.md` / `todo.md`) before answering from the code
alone — the docs carry the reasoning and history the code can't show.
If the docs turn out to be stale relative to the code, say so and fix them:
staleness discovered is staleness to repair.
