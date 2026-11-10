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
  when a risk/limitation/idea surfaces worth writing down, when the user
  asks why a past decision was made (read decisions.md before answering),
  when they want to see or visualize the code flow, or when they ask to
  "upgrade the brain flow doc". Team use too: "sync the brain" with
  teammates' commits, "why was this commit made", "backfill the brain".
---

# brain-docs — a living project memory

Chat sessions end; the reasoning behind code shouldn't. This skill maintains a
`brain/` folder of three documents that together act as the project's memory:

| File | Holds | Answers |
|---|---|---|
| `brain/decisions.md` | Dated decision log (newest first) — the project's *history* | "Why is it built this way?" |
| `brain/flow.md` | Snapshot of how the code executes *today* | "What calls what, in what order?" |
| `brain/todo.md` | Tagged action items, caveats, ideas | "What's known-broken, known-limited, or worth doing?" |

Alongside them sits `brain/flow-viewer.html` ("Tracer"), a single-file page
that renders each flow as a step-through trace timeline: one swimlane per
architecture layer, steps grouped into phases, and a detail panel with the
plain-English explanation, what the step passes on, what happens if it fails,
and a live source excerpt. A presentation mode swaps function names for plain
English for non-engineers. It also keeps call-tree and graph views, a file
index and a lint report.

The system only works if the docs are updated **incrementally, as you work** —
not in a batch when someone remembers to ask. A future session (or a future
maintainer) relies on them being current.

There are three modes. Check the project root:
- **No `brain/` folder, or the user asks to set one up → Setup mode.**
- **`brain/flow.md` is in the legacy format → Upgrade mode** (see below for
  how to detect it). Offer the upgrade; don't silently keep extending a
  legacy file.
- **Otherwise `brain/` exists → Maintain mode.**

A brain is either **solo** (one `decisions.md`, described first) or **team**
(`brain/decisions/` exists). In a team brain, read "Team mode" below as well:
it changes how decisions are stored and adds **Sync** and **Backfill**.

---

## Setup mode

1. **Create `brain/`** in the project root and seed the three files from
   `assets/templates/` (in this skill's folder). Adapt each file's title line
   to the project's name; keep the maintenance blockquotes — they remind
   future sessions of the rules even if this skill doesn't load.

2. **Ask who the brain is for: solo or team.** If several people work in the
   repo and more than one of them will use the brain, set up a team brain:
   follow "Team mode → Team setup" after these steps (it is always
   committed, so skip the question below). Otherwise it is a solo brain:
   **ask whether `brain/` should be git-ignored.** Don't assume — this is a
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

4. **Seed `flow.md` with a real trace** in the format described under
   "`brain/flow.md`" below. Explore the codebase and write the actual entry
   points and call paths — a skeleton with placeholders has no value until
   it describes the real system. Start with the Overview `components` block
   and the primary flow; add one `## Flow:` section per other entry point.
   If the codebase is large, trace the primary path end-to-end first and add
   a 🔴 todo naming the areas still unmapped. Only skip this (leaving the
   template + a 🔴 todo item to do it later) if the user asks to skip it.

5. **Install the viewer:** copy `assets/viewer/flow-viewer.html` to
   `brain/flow-viewer.html`. Tell the user how to open it: double-click it
   and pick `flow.md` once (Chrome/Edge remember the file and live-reload
   it), or serve the **project root** (`python -m http.server` there, then
   open `http://localhost:8000/brain/flow-viewer.html`). Served that way it
   loads `flow.md` on its own and can show source excerpts for each step.

6. `decisions.md` starts empty of entries (the first real decision will
   arrive soon enough). If the setup itself involved choices worth recording
   — e.g. the user picked committed-vs-ignored for a specific reason — that
   can be the first entry.

For the precise shape of each file, see the templates; for what good entries
look like, read `references/examples.md`.

---

## Upgrade mode — legacy `flow.md`

Older versions of this skill produced a flow.md that grows without bound:
`[CHANGED: …]` / `[NEW]` tags never cleared, rationale and history written
into call trees, paragraph-length nodes. On real projects it reached 1,000+
lines and stopped being readable or trustworthy.

**Detect it:** `brain/flow.md` contains `[CHANGED` or `[NEW` tags, or has no
` ```flow ` fenced blocks. (The viewer shows a "Legacy format" banner too.)

**Upgrade it** (ask first — it's a rewrite of a file the user relies on):

1. Rename the old file to `brain/flow.old.md`. It is a *map of what exists*,
   not a source of truth — parts of it are usually stale.
2. **Re-trace from the code** into the current format: list the entry points
   (routes, pages, CLI commands, jobs, event handlers), group them into
   flows, and verify every node against the source before writing it. Never
   copy a call tree across without checking it.
3. **Rescue, don't drop:** rationale found in the old doc that isn't in
   `decisions.md` yet becomes a D/W/A/T entry (date it to when the decision
   was made if the old doc says, otherwise today with "(recovered from
   flow.md)"). Caveats, dead code and limitations become `todo.md` items.
4. Install or refresh `brain/flow-viewer.html`, and check the viewer's Lint
   page (or the budgets below) is clean.
5. Update the project's `CLAUDE.md` standing-rule block to the current
   `assets/claude-md-snippet.md` wording — the old block is what told
   sessions to add `[CHANGED]` tags.
6. Tell the user `flow.old.md` can be deleted once they're happy, and log
   the upgrade in `decisions.md`.

For a very large codebase, trace the primary flow fully first, then the
rest one area at a time; track unfinished areas as a 🔴 todo rather than
leaving half-converted legacy text in the new file.

---

## Maintain mode

Update the docs **before ending any turn** in which you changed code, made a
decision, or learned something worth keeping. Match each file's existing
structure and tone. If one of the three files is missing, recreate it from
its template. If `brain/flow-viewer.html` is missing, or its
`<meta name="brain-docs-viewer" content="N">` version is lower than the copy
in this skill's `assets/viewer/`, copy the skill's version over it.

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

### `brain/flow.md` — a snapshot of the current code

**flow.md describes how the code executes right now — nothing else.** It is
not a changelog and not a design doc. History lives in `decisions.md` and
git; known problems live in `todo.md`. A reader should be able to trust every
line of it as true of today's code.

**Updating = re-trace and replace.** When a change alters how execution
travels (a new endpoint/page/job, a new or removed call in a path, a moved
function, a new provider), open the affected `## Flow:` section, re-read the
code path, and **rewrite that block so it matches the code**. Delete nodes
for deleted code. Never append a note explaining what changed.

**Banned in flow.md** — each of these is how the legacy format rotted:
- `[CHANGED: …]`, `[NEW]`, `[REMOVED]` or any other change tag
- dates, and history words: *was, previously, no longer, used to, old,
  supersedes, removed, deleted, now (as in "now does X")*
- rationale ("because…", "deliberately…", "so that…") → `decisions.md`
- bugs, caveats, dead code, TODOs → `todo.md`

**The format** (the viewer parses it, so stick to it exactly):

````markdown
# Execution Flow — <Project>

## Overview
```components
Browser -> API : REST
API -> Postgres : SQL
```

```layers
Browser : web/src
API     : api/routes, api/services
Jobs    : api/jobs
```

## Flow: Checkout {#checkout}
Trigger: user clicks "Pay" on /cart

```flow
== In the browser — check the cart, send it off
web/src/cart/CartPage.tsx :: onPay()  — validate cart, show spinner
  | plain: Checks the basket is still valid and starts the payment.
  web/src/lib/api.ts :: createOrder(cart)
    | passes: OrderRequest { items[], coupon? }
    => POST /api/orders
      == On the server — price it, save it, confirm it
      api/routes/orders.py :: create_order()
        api/services/pricing.py :: price_cart()
          | plain: Works out the final price, including any discount.
          | passes: PricedCart { lines[], total }
        [if coupon] apply_coupon()  — discount line items
        @payment
        db: INSERT orders
        ~ api/jobs/email.py :: send_receipt()
          | fails: A mail outage is retried in the background; the order still succeeds.
  [if API error] showToast()
```

## Key files
| Concern | Files |
|---|---|
| Orders API | `api/routes/orders.py`, `api/services/pricing.py` |
````

Grammar:
- **One call per line; 2-space indent = "calls", in source order.**
- `path :: symbol` — a call. A bare `symbol()` means "in the parent's file".
- ` — note` after a node (≤ 80 chars): *what* the hop does, never *why*.
- `=> METHOD /path`, `=> WS /path` — a process / network boundary.
- `db:` `ext:` `cache:` `queue:` `fs:` `env:` `log:` — side-effect leaves.
- `→ value` — what the step returns or responds with (`→ 401`, `→ None`).
- `[if cond]` / `[else]` — branch; `~` — async / background work.
- `@flow-id` — "continues in that flow" (each flow has a `{#id}`).
- `# …` at the end of a line is a comment the viewer ignores.

Trace extras (optional; they drive the viewer's timeline):
- ` ```layers ` under `## Overview`: one line per architecture layer,
  `Name : path/prefix, other/prefix`, in left-to-right lane order. A step goes
  in the layer whose prefix matches its path most specifically (a single file
  path works as a prefix too). Without it, each top-level folder is a layer.
- `== Phase name — short subtitle` inside a flow block starts a phase: a
  narrative chapter of the trace ("Through the gateway — let it in, work out
  who's asking"). Without phases, runs of steps in the same layer are grouped.
- `| plain: …`, `| passes: …`, `| fails: …` on the lines under a step attach
  to that step:
  - `plain` (≤ 120 chars): one sentence a non-engineer understands, with **no
    identifiers**: "A doorman: too many requests from one address and it turns
    you away", not "rate-limits per IP". Presentation mode shows it in place of
    the function name; without it, the note is used.
  - `passes` (≤ 80): names the **artefact** handed on, not the action:
    `ScoredCandidate[] sorted best-first`, not "returns the scores". Without
    it, the step's first unconditional `→ result` is used.
  - `fails` (≤ 160): **real** degradation behaviour ("Redis down → logs and
    lets the request through"). Leave it off when a failure is just a loud
    error.
  Add these to the steps that matter most (the primary flow, the boundaries,
  anything that degrades), not to every helper.

Shape and budgets:
- `## Overview` holds one ` ```components ` block (`A -> B : label`, `<->`
  for two-way) for the big picture, plus at most two sentences.
- One `## Flow:` section per entry point or user-visible action, each with a
  `Trigger:` line. **≤ 40 lines per flow block**, not counting `==` and `|`
  lines. Past that, move a stable
  sub-path into its own flow and reference it with `@id`. Shared paths (auth,
  the core engine) belong in one flow that others `@` reference, not copied.
- `## Key files` is a lookup table: ≤ 3 paths per row, no prose.
- **No cap on total file length** — let it grow with the project. Keep each
  flow tight instead: cut bloated notes before splitting flows.
- Trace the paths that matter (entry points, cross-module calls, boundaries,
  side effects); skip trivial helpers and getters.

Before ending the turn, check the touched flows' `Trigger`, `@refs` and Key
files rows still hold, and fix anything stale you notice elsewhere —
staleness discovered is staleness to repair. The `| plain/passes/fails`
lines describe the code too, so re-check them when you re-trace a step. The
viewer's **Lint** page checks the budgets, banned wording, broken `@refs`,
unknown `|` keys, identifiers in `plain`, and steps that match no layer.

### `brain/todo.md` — action items, caveats, ideas

- **Add** anything that surfaces while working: correctness or security
  risks noticed while reading (even in code you weren't asked to touch),
  by-design limitations worth remembering, feature ideas, tech debt.
- **Organize by topic, not by date.** Group items under functional-area
  headings (e.g. "Deploy & ops", "Backend / API", "Frontend / UI", "Tech
  debt") so the list stays scannable as it grows. A short list can stay flat;
  split it into topic sections once it gets long. **Never** create dated
  session sub-headings — a date belongs in the item's `(session …)` provenance
  tag, not in a header. (Date-grouping is exactly what turns a todo file into
  an unnavigable pile.)
- **Severity is an inline tag, not a header.** Every item carries one of these
  emoji (and, where possible, a `file:line` ref):

  - 🔴 **action required** — blocks something; must be done (deploy steps,
    migrations, missing config).
  - 🟠 **correctness / security** — observed risk; verify and fix.
  - 🟡 **known limitation** — by design; remember it, don't "fix" it blindly.
  - 🟢 **feature** — improvement idea.
  - 🔵 **tech debt** — cleanup that can wait.

- **When you complete an item**, check it off (`[x]`) and **move it to
  `brain/archive.md`** — the shipped archive, mirroring the same topic
  sections — so the working list stays lean. Create `archive.md` the first
  time you need it (it isn't seeded at setup). Delete an item outright only
  when it's obsolete rather than done.
- Mark provenance when useful: `(session)` for items surfaced while working
  vs. items imported from a roadmap or handoff doc.

### The cross-file rule

One piece of work often touches all three: if a task fixes a caveat listed in
`todo.md` **and** embodies a decision, then check it off in `todo.md`, log
the reasoning in `decisions.md`, and re-trace the affected path in `flow.md`
(replacing the block — the *why* and the *before* go in `decisions.md` only).
Ask "which of the three does this change concern?" every time — the honest
answer is frequently "more than one".

---

## Team mode

For a repo where several people commit and a few of them (often 2-3 of 10-15)
use the brain. Two things change. Decisions are stored so that brain users
never collide. And the brain accounts for **every commit on the main branch**,
including the ones written by teammates who have never heard of it.

**Nobody outside the brain users has to do anything.** No commit trailers, no
hooks, no CI. All linkage lives inside `brain/`. Never ask a teammate to
change how they commit, and never add tooling that runs for them.

### Layout

```
brain/
├── brain.json           branch + baseline commit (written once, never edited)
├── decisions/           one file per decision
├── ledger/              commits that need no decision entry
├── decisions-index.md   generated, git-ignored
├── tools/brain.py       the helper script
├── flow.md  todo.md  archive.md  flow-viewer.html      (as in solo mode)
```

There is no `brain/decisions.md` in a team brain; don't recreate it when
Maintain mode says to restore missing files.

### Decision entries

One file per decision: `brain/decisions/YYYY-MM-DD-short-slug.md`, from
`assets/templates/decision-entry.md`. The body is the same D/W/A/T. The
frontmatter is what makes it a team record:

- `author`: who did the **work** (the commit author), not who wrote the entry.
- `area`: one word, matching a `flow.md` layer or a `todo.md` topic.
- `commits`: SHAs on the main branch this entry explains. Empty until landed.
- `pr`: the pull request number, if any.
- `source`: `session` (written while doing the work), `inferred` (written
  later from someone else's commits), or `backfill`.
- `status`: `active`, or `superseded-by: <entry-id>` when a later entry
  reverses it. Supersede, don't delete: the old reasoning is still history.

Never append to someone else's entry. A new decision is a new file.

### The ledger and coverage

A commit is **covered** when its SHA is in an entry's `commits:` or in a
ledger row. Merge commits and commits that only touch `brain/` are covered
automatically. Everything on the main branch after the baseline should be
covered; `pending` lists what isn't.

Ledger rows are for commits that are real but don't embody a decision
(`minor`) or carry no meaning at all (`mechanical`). They live in
`brain/ledger/YYYY-MM.<your-handle>.md`: sharded by month and by who recorded
them, so two people syncing at once never edit the same file. Add rows with
the script, not by hand, so the shard and format stay right.

### The script

`python brain/tools/brain.py <command>` (standard library only; it reads git
and writes only inside `brain/`):

| Command | Use |
|---|---|
| `pending [--count]` | uncovered commits since the baseline, as a digest grouped by PR |
| `ledger auto` | record the commits `pending` marked `[mechanical? …]`, unread |
| `ledger add <sha…> --area X --what "…" [--kind mechanical]` | record commits that need no entry |
| `impact [A..B \| sha]` | flows in `flow.md` touched by the changed files (default: all uncovered commits) |
| `find --area/--author/--sha/--path/--text/--source` | look up entries and ledger rows |
| `index` | rebuild `decisions-index.md` and report likely duplicate entries |
| `init`, `migrate` | setup and solo → team conversion |

`pending` and `ledger auto` take `--range A..B`, `--since DATE`, `--last N`,
`--all` and `--path P` to look outside the default baseline-to-main range.

If `brain/tools/brain.py` is missing, or its `# brain-docs-tools: N` line is
lower than the copy in this skill's `assets/tools/`, copy the skill's version
over it. If Python isn't available, do the same job by hand: list commits
with `git log --reverse --date=short --stat <baseline>..<branch>` (the
baseline is in `brain/brain.json`) and treat a commit as covered when its
short SHA appears anywhere under `brain/decisions/` or `brain/ledger/`.

### Your own work

Work as in Maintain mode, with one difference: a meaningful decision becomes
a new file in `brain/decisions/` with `source: session` and `commits: []`
(the final SHAs don't exist until the work lands, and squash merges rewrite
them). Put the PR number in `pr:` once there is one. When the work reaches
the main branch it shows up in `pending`; add its SHAs to the entry you
already wrote. Don't write a second entry for it.

### Sync mode — absorbing everyone else's commits

Run it when the user says "sync the brain" (or similar), and at the start of
a session when `pending --count` is above zero: sync straight away if it is
10 or fewer, otherwise tell the user the number and offer. Sync works on the
local main branch, so check it is up to date first (ask before pulling).

1. **Read the digest:** `brain.py pending`. It prints up to 40 commits,
   oldest first; work in batches rather than loading a huge backlog.
2. **Clear the mechanical ones unread:** `brain.py ledger auto`.
3. **Link your own:** for commits that belong to an existing `session` entry
   (match by PR number, author and files), add the SHAs to its `commits:`.
4. **Triage the rest, one PR/group at a time.** The commit message is in the
   digest. If `gh` is installed and authenticated, `gh pr view <n>` gives the
   PR description and review discussion, which is usually where the *why*
   is. Open the diff (`git show <sha>`) only when the message is too thin to
   classify or the commit touches a traced flow.
   - It embodies a decision (new dependency, changed approach, a reversal,
     a new boundary, a revert of real work) → write an entry with
     `source: inferred`, `author:` the commit author, and the SHAs.
   - Otherwise → `brain.py ledger add`.
5. **Don't invent reasons.** You weren't there. **W**, **A** and **T** may
   only say what the commit message, PR, linked issue or code comments say.
   Where they are silent, write `not stated` and add a 🟡 todo
   "Confirm why … with @author" pointing at the entry. A wrong reason in the
   log is worse than a missing one, because later sessions will trust it.
6. **Repair the flow:** `brain.py impact` lists the flows whose traced files
   changed, deleted or renamed paths in Key files, and changed files that no
   flow mentions. Re-trace the listed flows from the code (replace the
   block, as always). For untraced files, add a flow only if they introduce
   an entry point or a cross-module path worth tracing.
7. **Carry over caveats:** risks or limitations you notice while reading go
   to `todo.md`, tagged `(sync)` and, when you know who owns it, `@handle`.
8. **Finish:** `brain.py index`, then `brain.py pending --count` should
   print 0 (or the size of the backlog you agreed to leave). If `index`
   reports a possible duplicate (two inferred entries for one commit, which
   happens when two people sync the same week), merge them into one file.
   Tell the user what was added. The brain changes are theirs to commit; a
   commit that touches only `brain/` never shows up as pending.

### Backfill mode — history from before the brain

Same procedure as Sync, over history older than the baseline, with
`source: backfill`. Run it only when asked, and never without scoping it:

1. Get the size: `brain.py pending --all --count`.
2. **Warn before starting:** backfilling reads a lot of history and consumes
   a lot of tokens, and reasons recovered from old commits are less reliable
   than ones written at the time. Give the count.
3. Agree a scope: the last N commits (`--last 200`), since a date
   (`--since 2026-01-01`), or one area (`--all --path api/payments`). A
   scoped backfill of the areas people still ask about beats a full one.
4. Sync that range, passing the same scope flags to `pending` and
   `ledger auto`. Be stricter than in a live sync: only write entries for
   decisions still visible in today's code, and ledger the rest.
5. Anything left unbackfilled stays uncovered and that is fine; it is
   outside the baseline, so the default `pending` never reports it.

### Team setup

After steps 1-6 of Setup mode (seed `flow.md`, `todo.md`, the viewer; do not
seed `decisions.md`):

1. Copy `assets/tools/brain.py` to `brain/tools/brain.py` and run
   `python brain/tools/brain.py init`. It records the main branch and the
   current tip as the baseline, and creates `decisions/`, `ledger/` and a
   `brain/.gitignore` for the generated index.
2. **Ask where the standing rule goes.** The shared `CLAUDE.md` makes every
   teammate's Claude sessions maintain the brain too. `CLAUDE.local.md`
   (personal, git-ignored) keeps it to the people who opted in; each brain
   user adds it to their own. When only a few people on the team use the
   brain, recommend `CLAUDE.local.md`. Install the **team** block from
   `assets/claude-md-snippet.md`.
3. **Offer a backfill, with the warning** from Backfill mode and the commit
   count `init` printed. Default to skipping it; the user can ask later.
4. `brain/` must be committed (that is how the brain users share it), so
   write for an audience: teammates can read every entry about their work.

### Solo → team

When the user asks to switch an existing solo brain: confirm `brain/` is (or
will be) committed, copy the script in, then run `brain.py migrate` followed
by `brain.py init`. `migrate` splits `decisions.md` into one file per entry
and keeps the original as `brain/decisions.solo.md`; check the entry count
it reports, set each entry's `area:` (they all start as `general`), then
delete the backup. Replace the standing-rule block with the team variant and
log the switch as a decision.

---

## Answering from the brain

When the user asks "why did we do X?", "how does Y work?", or "what's still
open?" in a project with a `brain/` folder, read the relevant doc
(`decisions.md` / `flow.md` / `todo.md`) before answering from the code
alone — the docs carry the reasoning and history the code can't show.
In a team brain, don't read every entry: use `brain.py find` (`--path` for
"why is this file like this", `--sha` for "why was this commit made",
`--area`, `--author`, `--text`) and open the files it lists. Say so when an
answer rests on an `inferred` or `backfill` entry or a `not stated` line.
If the docs turn out to be stale relative to the code, say so and fix them:
staleness discovered is staleness to repair. If the user wants to *see* the
flow, point them at `brain/flow-viewer.html`.
