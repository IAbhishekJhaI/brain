# Standing-rule block for the project's CLAUDE.md

Insert the block below into the project's `CLAUDE.md` (create the file if it
doesn't exist). Adapt the intro sentence to fit the surrounding file. This
block is what keeps the brain docs alive: `CLAUDE.md` loads every session
unconditionally, so the update discipline must live here, not only in the
skill.

---

## ⚠️ ALWAYS: keep the `brain/` docs current (highest-priority standing rule)

The `brain/` folder is the living memory of this project. **Whenever you
change or write code, or learn something worth keeping, update these three
files before you end your turn.** If a file is missing, recreate it (the
`brain-docs` skill has the templates and the viewer). Match the existing
structure and tone in each file.

Update them **incrementally as you work**, not only when asked. These docs
are relied on to survive across chat sessions.

### `brain/decisions.md` — the decision log
Append (newest-first, under a dated heading) an entry for **every meaningful
decision**: library/pattern/tradeoff choices, why an alternative was
rejected, mid-implementation reversals. Use the **D / W / A / T** format
(Decision · Why · Alternative rejected · Tradeoff accepted). Skip trivial
mechanical edits; capture anything a future maintainer would ask "why?"
about. Don't relitigate decisions already settled here.

### `brain/flow.md` — snapshot of the CURRENT code
flow.md says how the code executes **today** — it is not a changelog. When a
change alters how execution travels (new endpoint/page/job, a call added or
removed, a function moved), **re-trace that `## Flow:` section from the code
and replace its block**; delete nodes for deleted code.
- **Never** write `[CHANGED]`/`[NEW]` tags, dates, or history wording
  ("was", "previously", "no longer", "supersedes", "removed"). The *why* and
  the *before* go in `decisions.md`; caveats and dead code go in `todo.md`.
- Keep the parseable format (` ```flow ` blocks: one call per line,
  `path :: symbol  — note`, 2-space indent = calls; `=>` boundary, `db:`/`ext:`
  side effects, `→` result, `[if …]`, `~` async, `@flow-id` refs). Notes ≤ 80 chars and
  say *what*, not *why*. Flows ≤ 40 lines.
- Optional trace extras the viewer uses: a ` ```layers ` block under
  Overview, `== Phase — subtitle` lines, and `| plain:` / `| passes:` /
  `| fails:` lines under a step (plain English with no identifiers; the
  artefact handed on; real failure behaviour). Keep them true when you
  re-trace a step.
- `brain/flow-viewer.html` renders it as a step-through trace; its Lint page
  flags violations.

### `brain/todo.md` — action items, caveats, ideas
- **Add** anything that surfaces: correctness/security risks noticed while
  reading, by-design limitations worth remembering, feature ideas, tech debt.
- **Organize by topic, not by date** — group items under functional-area
  headings, keep each item's severity emoji as an inline tag (🔴 action ·
  🟠 correctness/security · 🟡 known limitation · 🟢 feature · 🔵 tech-debt) and
  a file:line ref. **No dated session sub-headings** — the date goes in the
  item's `(session …)` tag.
- When you complete an item, check it off (`[x]`) and **move it to
  `brain/archive.md`** (same topic sections) so the working list stays lean.

> If a task both fixes a caveat listed here **and** embodies a decision,
> update all three: check it off in `todo.md`, log the reasoning in
> `decisions.md`, and re-trace it in `flow.md` (replace, don't annotate).

---

# Team variant

For a team brain (`brain/decisions/` exists), use the block above with its
`brain/decisions.md` section **replaced** by the two sections below. Put the
whole block in the shared `CLAUDE.md`, or in each brain user's
`CLAUDE.local.md` when only some of the team uses the brain.

---

### `brain/decisions/` — one file per decision
This is a team brain: there is no `decisions.md`. Write each meaningful
decision as its own file, `brain/decisions/YYYY-MM-DD-short-slug.md`, with
D / W / A / T in the body and this frontmatter: `date`, `author` (who did the
work), `area`, `commits: []`, `pr`, `source: session`, `status: active`.
Never edit a teammate's entry; to reverse one, write a new entry and set the
old one's `status: superseded-by: <new-entry>`. Look entries up with
`python brain/tools/brain.py find --path <file>` (or `--sha`, `--area`,
`--author`, `--text`) rather than reading the folder.

### Commit coverage — every commit on main is accounted for
Most commits here come from teammates who don't use the brain. **They are
never asked to do anything**: no trailers, hooks or CI.
- **At session start** run `python brain/tools/brain.py pending --count`.
  Above zero means commits have landed that the brain doesn't explain yet.
  Sync right away if it is 10 or fewer; otherwise say the number and offer.
- **To sync**, follow the `brain-docs` skill's Sync mode: `pending` for the
  digest, `ledger auto` for mechanical commits, link your own landed commits
  to the entries you already wrote, write `source: inferred` entries for
  teammates' real decisions, `ledger add` for the rest, then `impact` and
  re-trace the flows it lists, then `index`.
- **Never invent a reason for someone else's commit.** If the commit, PR or
  code doesn't say why, write `not stated` and add a todo to confirm with
  the author.
- Backfilling history older than the baseline is expensive in tokens: only
  on request, after giving the commit count and agreeing a scope.
