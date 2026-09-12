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
| `brain/flow.md` | Whole-system execution flow (call trees + `[CHANGED]` tags) | "What calls what, in what order?" |
| `brain/todo.md` | Topic-grouped, severity-tagged action items, caveats, ideas (🔴🟠🟡🟢🔵) | "What's known-broken, known-limited, or worth doing?" |

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

**Maintain mode** — in a project that has `brain/`, it enforces the update
discipline: log meaningful decisions in D/W/A/T format, re-trace changed
execution paths, tag new risks and check off finished todos — incrementally,
before the turn ends, not in a batch when someone remembers to ask.

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
   ```

2. **Decide: ignore or commit.** Add `brain/` to your `.gitignore` if you
   want candid, local-only notes; leave it tracked to share the memory with
   your team. Both are valid.

3. **Install the standing rule.** Paste the block from
   [`brain-docs/assets/claude-md-snippet.md`](brain-docs/assets/claude-md-snippet.md)
   into your project's `CLAUDE.md` (create the file if it doesn't exist).
   **This step is what makes the system self-sustaining** — `CLAUDE.md` loads
   every session, so Claude keeps the docs updated without being reminded.

4. **Fill in `flow.md`.** The template ships with placeholders; ask Claude to
   "trace this codebase into brain/flow.md" (or write it yourself). A skeleton
   with no real trace has no value — this is the one file that needs seeding
   with actual content.

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
- **`brain/flow.md`** → *"What calls what, in what order?"* (call trees + `[CHANGED]` tags)
- **`brain/todo.md`** → *"What's broken / limited / worth doing?"* (grouped by topic, 🔴🟠🟡🟢🔵 tagged; completed items move to an optional `brain/archive.md`)

## Repo layout

```
brain-docs/            ← the skill (copy/package this folder)
├── SKILL.md           ← the instructions Claude follows
├── assets/
│   ├── templates/     ← seeds for decisions.md, flow.md, todo.md
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
