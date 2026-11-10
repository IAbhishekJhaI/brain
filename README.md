# brain-docs 🧠
- **The brain of your project**

**A Claude skill that gives your project a memory that survives across chat sessions.**

Chat sessions end. Context windows fill up. The reasoning behind your code —
why you picked library A over B, what that weird workaround protects against,
which TODO is actually load-bearing — evaporates every time. `brain-docs`
fixes that with a `brain/` folder of three living documents that Claude keeps
current *as it works*:

| File | Holds | Answers |
|---|---|---|
| `brain/decisions.md` | Dated decision log (newest first, **D/W/A/T** format) | "Why is it built this way?" |
| `brain/flow.md` | Snapshot of the *current* execution flow, as compact call trees | "What calls what, in what order?" |
| `brain/todo.md` | Topic-grouped, severity-tagged action items, caveats, ideas (🔴🟠🟡🟢🔵) | "What's known-broken, known-limited, or worth doing?" |

…plus **`brain/flow-viewer.html`**, a single-file visualizer for `flow.md`.
It draws each flow as a step-through trace timeline with layer swimlanes,
phases, failure notes and a presentation mode for non-engineers. It also has
call-tree and graph views, a component overview, jump-to search, a file index
and a lint report. No build step, and it works offline.

Start a fresh session weeks later, and Claude can answer "why did we reject
the fallback provider?" or "what's still blocking the deploy?" from the docs
— no archaeology through git history or old chats.

## Sound familiar?

- Don't understand the flow of the project you vibe-coded anymore? Which
  function calls what, in what order?
- No idea why the coding agent made *that* particular decision — what the
  alternatives were, what tradeoffs it accepted?
- Burning half your context window every session just getting the agent
  back up to speed?

Get any agent up to date on your project — its flow, its constraints, the
*why* behind every decision — in seconds. That's what `brain-docs` is for.

## What the skill does

**Setup mode** — in a project without a `brain/` folder, it:
1. Creates `brain/` and seeds the three files from templates
2. Asks whether to git-ignore it (candid local notes) or commit it (team-shared memory)
3. Installs a standing rule into your `CLAUDE.md` so the docs get updated
   every session — even sessions where the skill itself never triggers
4. Traces your actual codebase into `flow.md` (not just a skeleton)
5. Drops `flow-viewer.html` into `brain/`

**Maintain mode** — in a project that has `brain/`, it enforces the update
discipline: log meaningful decisions in D/W/A/T format, re-trace changed
execution paths (replacing them, not annotating them), tag new risks and
check off finished todos — incrementally, before the turn ends, not in a
batch when someone remembers to ask.

**Upgrade mode** — if `brain/flow.md` was written by an older version of
the skill (`[CHANGED]` tags, history mixed into the call trees), it re-traces
the code into the current format, moves any rationale it finds into
`decisions.md` and caveats into `todo.md`, and keeps the old file as
`flow.old.md` until you delete it. Trigger it with *"upgrade the brain flow
doc"*.

**Team mode** — for a repo where 10-15 people commit and a few of them use
the brain. Decisions become one file each (so brain users never collide),
and the brain accounts for **every commit on the main branch**, including
the ones from teammates who have never heard of it. See
[Team mode](#team-mode) below.

### Why flow.md is a snapshot, not a log

Earlier versions tagged every edit `[CHANGED: <area>]` and never removed the
tags. On a real project that produced a 1,200-line, 115 KB flow.md with 248
tags, where every node carried its own history ("the old one was…",
"supersedes…", "no longer reached from the UI") and the end-to-end trace
still described a provider that had since been replaced. Nobody could read
it, and nobody could trust it.

The rule now: **flow.md describes only the code as it runs today.** Changing
code means re-tracing the affected flow and replacing its block. History
already has homes: `decisions.md` (the *why* and the *before*) and git.
Budgets (≤ 80-char notes, ≤ 40-line flows) keep it
readable, and the viewer's lint page flags anything that slips.

### The D/W/A/T format

Every meaningful decision gets four lines:

- **D** — the **D**ecision: what was done, naming the exact files and seams
- **W** — **W**hy: the need or problem that drove it
- **A** — the **A**lternative rejected, and why it lost *(this is the line
  that stops future sessions from relitigating settled choices)*
- **T** — the **T**radeoff accepted: what got worse, and why that's OK

## Install

### Option 1: `.skill` file (recommended)
1. Download `brain-docs.skill` from the [latest release](../../releases).
2. In Claude, go to **Settings → Skills → Add skill** (top right) →
   **Upload skill** → select the `brain-docs.skill` you downloaded.

*(Alternatively, drop the unzipped `brain-docs/` folder straight into your
`~/.claude/skills/` directory — on Windows, `%USERPROFILE%\.claude\skills\` —
and Claude Code picks it up on the next session.)*

### Option 2: copy the folder (Claude Code)
Clone this repo and copy the inner `brain-docs/` folder into your skills
directory:

```bash
# macOS / Linux
git clone https://github.com/IAbhishekJhaI/brain.git
cp -r brain/brain-docs ~/.claude/skills/brain-docs
```

```powershell
# Windows (PowerShell)
git clone https://github.com/IAbhishekJhaI/brain.git
Copy-Item -Recurse brain\brain-docs "$env:USERPROFILE\.claude\skills\brain-docs"
```

For a single project instead of all projects, copy it to
`<project>/.claude/skills/brain-docs`.

### Option 3: just steal the idea
The whole system is three markdown formats and one CLAUDE.md rule — no skill
required. See **Manual setup** below.

## Setup

### With the skill (recommended)

Once installed (Option 1 or 2 above), open the project you want a brain for
and just type:

> **set up a project brain for the repo**

That's the whole trigger — no slash command. Skills are invoked by describing
the task in plain language; Claude reads the skill's description, sees the
match, and runs it. The skill will:

1. Create `brain/` with the three seeded files
2. Ask whether to git-ignore `brain/` (candid local notes) or commit it
   (team-shared memory) — your call
3. Add the standing rule to your `CLAUDE.md` (creating it if needed)
4. Trace your actual codebase into `flow.md`
5. Copy the viewer to `brain/flow-viewer.html`

**You only do this once per project.** After setup, the standing rule lives in
`CLAUDE.md` (which Claude loads every session automatically), so the docs keep
loading, updating, and staying current across every future session on their
own — no need to re-run anything.

### Manual setup (no skill)

The system is portable by hand in four steps:

1. **Create the folder and seed the three files.** Copy the templates from
   [`brain-docs/assets/templates/`](brain-docs/assets/templates/) into a new
   `brain/` directory at your project root:

   ```bash
   mkdir brain
   cp path/to/brain-docs/assets/templates/decisions.md brain/
   cp path/to/brain-docs/assets/templates/flow.md      brain/
   cp path/to/brain-docs/assets/templates/todo.md      brain/
   cp path/to/brain-docs/assets/viewer/flow-viewer.html brain/
   ```

2. **Decide: ignore or commit.** Add `brain/` to your `.gitignore` if you
   want candid, local-only notes; leave it tracked to share the memory with
   your team. Both are valid.

3. **Install the standing rule.** Paste the block from
   [`brain-docs/assets/claude-md-snippet.md`](brain-docs/assets/claude-md-snippet.md)
   into your project's `CLAUDE.md` (create the file if it doesn't exist).
   **This step is what makes the system self-sustaining** — `CLAUDE.md` loads
   every session, so Claude keeps the docs updated without being reminded.

4. **Fill in `flow.md`.** The template ships with placeholders and a grammar
   cheat-sheet; ask Claude to "trace this codebase into brain/flow.md" (or
   write it yourself). A skeleton with no real trace has no value — this is
   the one file that needs seeding with actual content.

For what good entries look like once you're maintaining the docs, see
[`brain-docs/references/examples.md`](brain-docs/references/examples.md).

## Use

After setup, just work normally — the `CLAUDE.md` rule prompts the updates.
Handy phrases:

- *"log this decision"* / *"update the brain docs"* — force an update mid-work
- *"why did we choose X?"* — Claude reads `decisions.md` before answering
- *"what's still open?"* — Claude reads `todo.md`

The three files answer three questions:

- **`brain/decisions.md`** → *"Why is it built this way?"* (dated D/W/A/T log)
- **`brain/flow.md`** → *"What calls what, in what order?"* (current-state call trees)
- **`brain/todo.md`** → *"What's broken / limited / worth doing?"* (grouped by topic, 🔴🟠🟡🟢🔵 tagged; completed items move to an optional `brain/archive.md`)

## Team mode

A solo brain assumes one person and one agent. On a team that breaks three
ways: most commits come from people who don't use the brain, so `flow.md`
goes stale and nothing records why; two people prepending to one
`decisions.md` conflict on every merge; and no entry says which commit it
explains.

Team mode fixes those for the people who use the brain, **without asking
anyone else to change anything**. No commit trailers, no hooks, no CI. Say
*"set up a team brain"* (or *"switch the brain to team mode"* in a repo that
already has a solo one).

```
brain/
├── brain.json           branch + baseline commit
├── decisions/           one file per decision, with author / commits / PR
├── ledger/              commits that need no decision entry
├── tools/brain.py       helper script (Python 3, standard library only)
└── flow.md  todo.md  flow-viewer.html
```

- **One file per decision.** `brain/decisions/2026-11-04-pricing-tiers.md`
  holds the usual D/W/A/T plus frontmatter: `author` (who did the work),
  `area`, `commits`, `pr`, `source` and `status`. Nobody edits anyone
  else's file, so there is nothing to conflict on.
- **Every commit is covered.** A commit on main is covered when a decision
  entry lists it or the ledger has a row for it. Merges and brain-only
  commits are covered automatically. The ledger is split by month and by
  who recorded the rows, so two people syncing the same week still don't
  touch the same file.
- **Sync** (*"sync the brain"*) absorbs teammates' commits: mechanical ones
  are recorded unread, real decisions become entries marked
  `source: inferred`, the rest get a ledger row, and every flow whose files
  changed is re-traced. Claude checks for unsynced commits at the start of
  each session.
- **No invented reasons.** For someone else's commit, the entry may only
  say what the commit, PR or code says. Where they are silent it says
  `not stated` and a todo asks the author.
- **Backfill** (*"backfill the brain from git history"*) does the same for
  history older than the brain. It reads a lot and costs a lot of tokens,
  so it runs only on request, after showing the commit count and agreeing a
  scope (last N commits, since a date, or one path).

The script does the bookkeeping so the agent doesn't spend tokens on it:

| Command | Does |
|---|---|
| `python brain/tools/brain.py pending` | commits the brain doesn't explain yet, grouped by PR |
| `… pending --count` | just the number |
| `… ledger auto` | record the obviously mechanical ones (lockfiles, formatting, docs) |
| `… ledger add <sha> --area api --what "…"` | record a commit that needs no entry |
| `… impact` | flows in `flow.md` touched by the changed files |
| `… find --path api/pricing.py` | entries about a file (also `--sha`, `--area`, `--author`, `--text`) |
| `… index` | rebuild the git-ignored `decisions-index.md` |
| `… init` / `… migrate` | start a team brain / split a solo `decisions.md` |

`brain/` is committed in team mode; that is how the brain users share it.
The standing rule can go in the shared `CLAUDE.md` (every teammate's Claude
keeps the brain up) or in each brain user's `CLAUDE.local.md` (only the
people who opted in).

## The flow.md format

Plain markdown that reads fine on GitHub, with fenced blocks the viewer
parses:

````markdown
## Flow: Checkout {#checkout}
Trigger: user clicks "Pay" on /cart

```flow
web/src/cart/CartPage.tsx :: onPay()  — validate cart, show spinner
  web/src/lib/api.ts :: createOrder(cart)
    => POST /api/orders
      api/routes/orders.py :: create_order()
        @payment
        db: INSERT orders
        ~ api/jobs/email.py :: send_receipt()
  [if API error] showToast()
```
````

One call per line, 2-space indent = "calls". `path :: symbol` is a call (a
bare `symbol()` lives in its parent's file), `— note` says what the hop does,
`=>` marks a network/process boundary, `db:` / `ext:` / `cache:` / `queue:`
mark side effects, `→ value` is what a step returns, `[if …]` is a branch,
`~` is async, and `@id` continues in another flow. A `## Overview` section holds a ` ```components ` block
(`A -> B : label`) for the big picture, and `## Key files` is a lookup table.

Optional extras turn a flow into a narrated trace in the viewer:

````markdown
```layers
Browser : web/src
API     : api/routes, api/services
```

```flow
== On the server — price it, save it
api/services/pricing.py :: price_cart()
  | plain: Works out the final price, including any discount.
  | passes: PricedCart { lines[], total }
  | fails: Tax service down → falls back to the cached rate table.
```
````

A ` ```layers ` block names the swimlanes and maps path prefixes to them.
`== Phase — subtitle` lines group steps into chapters. `| plain:` (jargon-free,
shown in presentation mode), `| passes:` (the artefact handed on) and
`| fails:` (real degradation behaviour) attach to the step above them. Full
rules are in [`SKILL.md`](brain-docs/SKILL.md).

## The visualizer

`brain/flow-viewer.html` ("Tracer") is one self-contained HTML file. It
needs no build step. It loads the IBM Plex fonts from Google Fonts when
online and falls back to system fonts offline. Otherwise it only reads
`flow.md` and, when served, your source files.

- **Open it:** double-click it, click **Open flow.md** and pick the file (or
  drag it onto the page). In Chrome and Edge the viewer remembers the file
  and **live-reloads** whenever it changes, so you can keep it open while
  Claude works. Other browsers load a static copy; press Open again to
  refresh.
- **Or serve the project root** for zero clicks and source excerpts: run
  `python -m http.server` in the project root and open
  `http://localhost:8000/brain/flow-viewer.html`. It auto-loads and
  live-reloads `flow.md`.

What you get:
- **Trace timeline** (the default for each flow): the flow drawn top to
  bottom as numbered steps, each card in the swimlane of the layer that runs
  it, grouped into phase bands. Step through it with `◀ ▶`, `←/→` or `j/k`;
  jump phases with `[ ]`.
- **Presentation mode** (`p`): cards show plain English instead of function
  names. The layout doesn't move, so you can switch mid-walkthrough.
- **Detail panel:** layer, file path, plain-English and technical
  descriptions, **If it fails**, **Passes on**, side effects, a source
  excerpt (when served from the project root), and **Calls / Called by**
  chips that explore sideways without losing your place.
- **Shareable links:** the URL keeps the flow, step, selection and
  presentation mode.
- **Jump to** (`⌘K` / `Ctrl-K` / `/`): search functions, files and
  plain-English descriptions across every flow.
- **Tree and Graph views** of the same flow, plus **Overview** (component
  diagram, traces, layers), **Files** (every traced file and its flows) and
  **Lint** (legacy tags, history wording, budgets, broken `@refs`, unknown
  `|` keys, identifiers in plain English, steps that match no layer).

## Repo layout

```
brain-docs/            ← the skill (copy/package this folder)
├── SKILL.md           ← the instructions Claude follows
├── assets/
│   ├── templates/     ← seeds for decisions.md, flow.md, todo.md, team decision entries
│   ├── viewer/
│   │   └── flow-viewer.html  ← the visualizer copied into brain/
│   ├── tools/
│   │   └── brain.py   ← team-mode helper copied into brain/tools/
│   └── claude-md-snippet.md  ← the standing rule for your CLAUDE.md
└── references/
    └── examples.md    ← worked examples of each format
```

## Provenance

Extracted from a real production workflow: an AI travel-planner project ran
this exact system for months — hundreds of D/W/A/T entries, a 700-line
whole-system flow doc, and a todo file that repeatedly caught deploy-blocking
config before it bit. The formats here are what survived contact with real
work, generalized for any project.
