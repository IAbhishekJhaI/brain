# brain-docs 🧠
- **The brain of your project**

[![Visitors](https://komarev.com/ghpvc/?username=IAbhishekJhaI&repo=brain&label=visitors&color=blueviolet&style=flat)](https://github.com/IAbhishekJhaI/brain)
[![Latest release](https://img.shields.io/github/v/release/IAbhishekJhaI/brain?style=flat)](https://github.com/IAbhishekJhaI/brain/releases/latest)
[![Downloads](https://img.shields.io/github/downloads/IAbhishekJhaI/brain/total?style=flat&label=.skill%20downloads)](https://github.com/IAbhishekJhaI/brain/releases)
[![License](https://img.shields.io/github/license/IAbhishekJhaI/brain?style=flat)](LICENSE)

Installation: paste this one line into Claude Code and it will do the setup for you:
```text
Read https://raw.githubusercontent.com/IAbhishekJhaI/brain/main/INSTALL-WITH-CLAUDE.md and follow it.
```

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
   every session automatically — even sessions where the skill itself never triggers
4. Traces your actual codebase into `flow.md` (not just a skeleton)
5. Logs every meaningful decision since setup into `decisions.md` and files to-do items
    uncovered by your agent into `todo.md`

**Upgrade mode** — Trigger it with *"upgrade the brain flow doc"* .
if `brain/flow.md` was written by an older version of
the skill (`[CHANGED]` tags, history mixed into the call trees), it re-traces
the code into the current format, moves any rationale it finds into
`decisions.md` and caveats into `todo.md`, and keeps the old file as
`flow.old.md` until you delete it.

**Team mode** — for a repo where 10-15 people commit and a few of them use
the brain. Decisions become one file each (so brain users never collide),
and the brain accounts for **every commit on the main branch**, including
the ones from teammates who have never heard of it. See
[Team mode](#team-mode) below.


### The D/W/A/T format

Every meaningful decision gets four lines:

- **D** — the **D**ecision: what was done, naming the exact files and seams
- **W** — **W**hy: the need or problem that drove it
- **A** — the **A**lternative rejected, and why it lost *(this is the line
  that stops future sessions from relitigating settled choices)*
- **T** — the **T**radeoff accepted: what got worse, and why that's OK

## Install

### Option 0: let Claude Code install it (easiest)
Open [`INSTALL-WITH-CLAUDE.md`](INSTALL-WITH-CLAUDE.md), copy the whole file,
and paste it into Claude Code. Claude downloads the skill, installs it for
all projects or just this one, checks the install, and offers to set up a
brain for the project you have open.

Or paste this one line into Claude Code:

```text
Read https://raw.githubusercontent.com/IAbhishekJhaI/brain/main/INSTALL-WITH-CLAUDE.md and follow it.
```

### Option 1: `.skill` file
1. Download `brain-docs.skill` from the [latest release](../../releases).
2. In Claude, go to **Settings → Skills → Add skill** (top right) →
   **Upload skill** → select the `brain-docs.skill` you downloaded.

*(Alternatively, drop the unzipped `brain-docs/` folder straight into your
`~/.claude/skills/` directory — on Windows, `%USERPROFILE%\.claude\skills\` —
and Claude Code picks it up on the next session.)*

## Setup

### With the skill (recommended)

Once installed, open the project you want a brain for
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

## The flow viewer

`brain/flow-viewer.html` turns `flow.md` into something you can
click through. It is one self-contained HTML file: no build step, no
install, works offline.

### Opening it

| How | What you get |
|---|---|
| **Double-click it** (Chrome / Edge) | Click **Open flow.md** once, or drag the file onto the page. The viewer remembers the file for this project and **live-reloads** it so you can keep it open while Claude works. On later visits it reopens the file by itself, or after a single **Reconnect** click. |
| **Double-click it** (other browsers) | Same picker and drag-and-drop, but a static copy: press **Open** again to refresh. |
| **Serve the project root** | `python -m http.server` in the project root, then open `http://localhost:8000/brain/flow-viewer.html`. Loads `flow.md` with no clicks, live-reloads it, and adds **source excerpts** to the detail panel. |

The dot in the header says **live** or **static**, and the reload button
re-reads the file on demand.

### Three ways to look at a flow

- **Trace** (the default): the flow as numbered steps from top to bottom.
  Each card sits in the swimlane of the layer that runs it (browser, API,
  worker…) and steps are grouped into numbered phase bands. A card shows
  the function, what it does, `if` / `else` and `async` tags, side-effect
  chips (`db:`, `ext:`, `cache:`, `queue:`) and what it **passes** on.
  Network and process hops appear as `⇄` boundary rows, and the flow's
  final result as a **RETURN** row. A step that continues in another flow
  shows as `↪ Flow name`; double-click it to go there.
- **Tree**: the same flow as an indented call tree. **Expand all**,
  **Collapse all**, **Depth 2** and **Depth 3** set how much you see; `▸`
  folds one branch. `@ref` steps unfold the referenced flow in place, with
  recursion detected.
- **Graph**: a left-to-right call graph. Drag to pan, scroll to zoom,
  double-click a box to fold its branch, **Fit** to see it all. Branch
  conditions label the edges, and async calls get their own edge style.

Layers come from the ` ```layers ` block under Overview. Without one, each
top-level folder becomes a layer.

### Reading a step

Click any step, in any view, to open the detail panel:

- the step's **layer**, its position (`step 4 of 12`), and any branch or
  async tag
- the **file path**, copied to the clipboard when clicked
- **In plain English** (from `| plain:`), with the technical note below it
- **If it fails** (from `| fails:`): what really happens when this step breaks
- **Passes on** (from `| passes:`): the artefact handed to the next step
- **Side effects**, and **Continues in** for steps that hand off to another flow
- **Source**: an excerpt of the function with an **open file ↗** link,
  when the viewer is served from the project root
- **Calls / Called by** chips to explore sideways without losing your place
  in the trace

### Presentation mode

Press `p` (or the toggle in the header) to swap function names for plain
English on every card. The layout doesn't move, so you can switch in the
middle of a walkthrough with a product manager, a designer or a new hire.

### Project pages

The sidebar lists every trace with its step count, the current flow's
phases (click one to jump to it) and its layers. Above them sit three
project-wide pages:

- **Overview**: the component diagram drawn from the ` ```components `
  block, a card for each trace (steps, phases, files, and which flows use
  it), and the layers table. Sections outside the flow format are shown as
  text, and an old-format `flow.md` gets a banner telling you to ask Claude
  to *"upgrade the brain flow doc"*.
- **Files**: the **Key files** table, plus every traced file with its layer
  and a chip for each flow that uses it. Click a chip to jump to that step.
- **Lint**: checks `flow.md` against the format, with line numbers. The
  sidebar badge shows the error or warning count at a glance.

| Lint level | Checks |
|---|---|
| **error** | legacy `[CHANGED]` / `[NEW]` tags · no `## Flow:` sections (old format) · broken `@ref` · unclosed code fence |
| **warn** | history wording ("previously", "no longer", "was", dates…) in notes, phases, triggers or Key files · notes over 80 chars · flows over 40 lines · `plain` / `passes` / `fails` over 120 / 80 / 160 chars · Key files rows with more than 3 paths, or that read like prose · indent not a multiple of 2 · unknown or malformed `\|` lines · blocks in the wrong section · duplicate flow ids or layers · a layer with no paths · a flow with no ` ```flow ` block |
| **info** | missing `Trigger:` line or `{#id}` · steps before the first `==` phase · empty phases · indent that skips a level · code identifiers in plain English · steps that match no layer · layers with no steps · sections outside the format |

### Getting around

| Key | Does |
|---|---|
| `←` `→` or `j` `k` | previous / next step (the `◀ ▶` buttons too) |
| `[` `]` | previous / next phase |
| `p` | presentation mode on / off |
| `⌘K`, `Ctrl-K` or `/` | **Jump to**: search functions, files and plain-English descriptions across every flow |
| `Esc` | clear the selection, or close the detail panel |
| `Enter` | select the focused step; in the tree, `←` `→` fold and unfold |

**Links are shareable.** The URL keeps the flow, step, selection and
presentation mode, so a link drops a teammate on exactly the step you mean.
On narrow screens the sidebar moves behind a menu button and the detail
panel opens as a sheet.

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

Extracted from a real production workflow: an AI agent project ran
this exact system for months — hundreds of D/W/A/T entries, a 700-line
whole-system flow doc, and a todo file that repeatedly caught deploy-blocking
config before it bit. The formats here are what survived contact with real
work, generalized for any project.
