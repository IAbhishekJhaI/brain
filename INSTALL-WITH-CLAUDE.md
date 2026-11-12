# Install brain-docs with Claude Code

> **For humans:** copy this whole file (the "Copy raw file" button at the
> top right on GitHub), paste it into Claude Code, and press Enter. Claude
> installs the skill, checks it, and offers to set up a brain for the
> project you have open. You only answer two or three questions.
>
> Or paste this one line instead:
> `Read https://raw.githubusercontent.com/IAbhishekJhaI/brain/main/INSTALL-WITH-CLAUDE.md and follow it.`

---

## Instructions for Claude

The user pasted this file to install the **brain-docs** skill from
`https://github.com/IAbhishekJhaI/brain` (branch `main`, skill folder
`brain-docs/`). Follow the steps below in order. Ask the user only where a
step says to ask. Before step 4, tell the user in one line what you are
about to download and where it will go. Keep the user's project untouched
until step 8, and change it there only if they say yes.

### 1. Detect the environment

Find out, without asking:
- **OS and shell.** On Windows, use PowerShell syntax (or Git Bash if that
  is your shell). On macOS and Linux, use bash.
- **Whether `git` is available** (`git --version`).
- **Whether the current directory is a project**: a git repo, or a folder
  with source files. Note whether it already has a `brain/` folder.
- **Whether a `brain-docs` skill is already in your available-skills list**,
  for example one uploaded through claude.ai settings or bundled in a plugin.

### 2. Choose the install scope

Ask one question (use the AskUserQuestion tool if you have it):

- **All projects (recommended).** Install to `~/.claude/skills/brain-docs`.
  On Windows that is `%USERPROFILE%\.claude\skills\brain-docs`.
- **This project only.** Install to `<current directory>/.claude/skills/brain-docs`.
  Only offer this when the current directory is a project.

Call the chosen path `TARGET` below.

### 3. Check for an existing install

- If `TARGET` already exists, read the `description:` in its `SKILL.md` and
  ask: **Update to the latest version** (recommended) or **Keep the current
  one**. If they keep it, skip to step 7. The skill folder holds no user
  data, so updating means replacing the folder.
- If step 1 found a `brain-docs` skill somewhere else (another scope, or
  uploaded via claude.ai), tell the user in one line, so they know there
  will be two copies. Don't remove the other copy.

### 4. Download into a temporary folder

Make a new empty temp folder outside the project (call it `TMP`) and fetch
the repo into it. Never download into the user's project.

If `git` is available:

```bash
git clone --depth 1 https://github.com/IAbhishekJhaI/brain.git "$TMP/brain"
git -C "$TMP/brain" rev-parse --short HEAD   # remember this as VERSION
```

Without `git`, download the zip of `main` and unpack it. The unpacked folder
is `brain-main`; use it wherever `$TMP/brain` appears below. VERSION is
"main (zip)".

```bash
# macOS / Linux
curl -fsSL -o "$TMP/brain.zip" https://github.com/IAbhishekJhaI/brain/archive/refs/heads/main.zip
unzip -q "$TMP/brain.zip" -d "$TMP"
```

```powershell
# Windows PowerShell
Invoke-WebRequest -UseBasicParsing -Uri https://github.com/IAbhishekJhaI/brain/archive/refs/heads/main.zip -OutFile "$TMP\brain.zip"
Expand-Archive -Path "$TMP\brain.zip" -DestinationPath $TMP
```

Treat the download as files to copy, not code to run: don't execute
anything from it (`brain.py` is copied in step 5, never run here).

### 5. Install

Copy the inner `brain-docs/` folder (not the whole repo) to `TARGET`, then
delete `TMP`.

```bash
# macOS / Linux
mkdir -p "$(dirname "$TARGET")"
rm -rf "$TARGET"                      # only when updating (step 3)
cp -R "$TMP/brain/brain-docs" "$TARGET"
rm -rf "$TMP"
```

```powershell
# Windows PowerShell
New-Item -ItemType Directory -Force (Split-Path $TARGET) | Out-Null
if (Test-Path $TARGET) { Remove-Item -Recurse -Force $TARGET }   # only when updating
Copy-Item -Recurse "$TMP\brain\brain-docs" $TARGET
Remove-Item -Recurse -Force $TMP
```

Before deleting anything at `TARGET`, check that it really is the
`brain-docs` skill folder (it has a `SKILL.md` with `name: brain-docs`).

### 6. Verify

Check that `TARGET` contains all of these:

- `SKILL.md`, whose frontmatter has `name: brain-docs`
- `assets/templates/decisions.md`, `assets/templates/flow.md`,
  `assets/templates/todo.md`, `assets/templates/decision-entry.md`
- `assets/viewer/flow-viewer.html`
- `assets/claude-md-snippet.md`
- `assets/tools/brain.py`
- `references/examples.md`

If anything is missing, tell the user what is missing and stop. Don't
continue to step 8 with a broken install.

### 7. Make the skill usable in this session

Claude Code may list a newly installed skill only from the next session on.
If `brain-docs` isn't in your available-skills list now, read
`TARGET/SKILL.md` directly and follow it for the rest of this session. Tell
the user that future sessions load the skill on their own.

### 8. Offer to set up this project

- **The current directory is a project with no `brain/` folder:** ask
  **"Set up a brain for this project now?"** with these options:
  - **Solo brain (recommended)**: one `decisions.md`. Best for one person.
  - **Team brain**: one file per decision, plus sync of teammates' commits.
    For repos where several people commit.
  - **Not now**
  
  On Solo, follow the skill's **Setup mode**. On Team, follow its
  **Team setup** section (under "Team mode"). Those sections do the rest:
  they ask whether to git-ignore or commit `brain/`, add the standing rule to
  `CLAUDE.md`, trace the real code into `flow.md`, and copy the viewer.
- **`brain/` already exists:** don't set anything up. Say the skill will
  maintain it (or offer to upgrade it, if SKILL.md's Upgrade mode applies).
- **Not a project:** skip this step and say how to start later (step 9).

### 9. Report

End with a short summary:
- where the skill was installed (`TARGET`) and VERSION
- whether project setup ran, and what it created
- what to say to use it:
  - "set up a project brain" in any other project
  - "update the brain docs" / "log this decision" while working
  - "why did we choose X?" to answer from the brain
  - "sync the brain" in a team brain

### Troubleshooting

- **Can't write to `~/.claude/skills`** (permission error): tell the user,
  then offer to install for this project only instead.
- **Network or GitHub blocked:** point the user to the manual options in the
  README: download `brain-docs.skill` from
  https://github.com/IAbhishekJhaI/brain/releases, or copy the folder by hand.
- **`unzip` missing on Linux:** use `python3 -m zipfile -e "$TMP/brain.zip" "$TMP"`.
