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
`brain-docs` skill has the templates). Match the existing structure and tone
in each file.

Update them **incrementally as you work**, not only when asked. These docs
are relied on to survive across chat sessions.

### `brain/decisions.md` — the decision log
Append (newest-first, under a dated heading) an entry for **every meaningful
decision**: library/pattern/tradeoff choices, why an alternative was
rejected, mid-implementation reversals. Use the **D / W / A / T** format
(Decision · Why · Alternative rejected · Tradeoff accepted). Skip trivial
mechanical edits; capture anything a future maintainer would ask "why?"
about. Don't relitigate decisions already settled here.

### `brain/flow.md` — whole-system execution flow
When a change alters how execution travels (new endpoint, new call in a
path, a stage's inputs/outputs, a provider, a frontend data path), update the
relevant call-tree section, the **Key files** table, and the end-to-end
trace. Tag edited spots inline with `[CHANGED: <area>]`. Keep it
whole-system, not session-scoped. If you add/rename a module or function,
fix its node here.

### `brain/todo.md` — action items, caveats, ideas
- **Add** anything that surfaces: correctness/security risks noticed while
  reading, by-design limitations worth remembering, feature ideas, tech debt.
- **Check off** (`[x]`) items you complete, and **remove** ones that no
  longer apply.
- Keep the severity tags (🔴 action · 🟠 correctness/security · 🟡 known
  limitation · 🟢 feature · 🔵 tech-debt) and file:line references.

> If a task both fixes a caveat listed here **and** embodies a decision,
> update all three: check it off in `todo.md`, log the reasoning in
> `decisions.md`, and re-trace it in `flow.md`.
