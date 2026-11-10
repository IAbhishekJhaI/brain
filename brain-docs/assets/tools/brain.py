#!/usr/bin/env python3
# brain-docs-tools: 1
"""brain.py — commit coverage and lookup for a team-mode brain/ folder.

Python 3 standard library only. Reads git, writes only inside brain/.

  init      record the baseline commit and main branch (brain/brain.json)
  pending   commits on the main branch that the brain doesn't account for yet
  ledger    record commits that need no decision entry (add / auto)
  impact    which flows in flow.md the changed files touch
  index     regenerate brain/decisions-index.md (git-ignored) from brain/decisions/*.md
  find      look up decision entries and ledger rows
  migrate   split a solo decisions.md into one file per entry

A commit is *covered* when its SHA appears in a decision entry's `commits:`
list or in a ledger row. Merge commits and commits that only touch brain/
are covered automatically.
"""
import argparse
import json
import os
import re
import subprocess
import sys

VERSION = 1
INDEX_NAME = "decisions-index.md"
SHA_RE = re.compile(r"^[0-9a-f]{7,40}$")
LOCKFILES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb", "bun.lock",
    "poetry.lock", "uv.lock", "Pipfile.lock", "Cargo.lock", "go.sum",
    "Gemfile.lock", "composer.lock", "flake.lock", "packages.lock.json",
}
DOC_EXT = (".md", ".mdx", ".rst", ".txt", ".adoc")
MECH_SUBJECT = [
    (re.compile(r"^(chore|style|ci|build)(\([^)]*\))?!?:", re.I), "chore"),
    (re.compile(r"^docs(\([^)]*\))?!?:", re.I), "docs"),
    (re.compile(r"^(bump|release|version)\b|^v?\d+\.\d+\.\d+\b", re.I), "version"),
    (re.compile(r"\b(prettier|reformat|formatting|lint fix|fix lint|typo|whitespace)\b", re.I), "format"),
]
PR_RE = [re.compile(r"^Merge pull request #(\d+)"), re.compile(r"\(#(\d+)\)\s*$"),
         re.compile(r"^Merged PR (\d+)")]


def die(msg):
    sys.stderr.write("brain.py: " + msg + "\n")
    sys.exit(2)


def git(*args, check=True):
    p = subprocess.run(["git", "-c", "core.quotepath=off"] + list(args),
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        if check:
            die("git %s failed: %s" % (" ".join(args[:2]), p.stderr.decode("utf-8", "replace").strip()))
        return None
    return p.stdout.decode("utf-8", "replace")


class Repo:
    def __init__(self):
        top = git("rev-parse", "--show-toplevel", check=False)
        if not top:
            die("not inside a git repository")
        self.root = top.strip()
        os.chdir(self.root)
        self.brain = os.path.join(self.root, "brain")
        self.decisions = os.path.join(self.brain, "decisions")
        self.ledger = os.path.join(self.brain, "ledger")
        self.cfg_path = os.path.join(self.brain, "brain.json")
        self.cfg = {}
        if os.path.exists(self.cfg_path):
            with open(self.cfg_path, encoding="utf-8") as f:
                self.cfg = json.load(f)

    def branch(self, override=None):
        if override:
            return override
        if self.cfg.get("branch"):
            return self.cfg["branch"]
        head = git("symbolic-ref", "--short", "refs/remotes/origin/HEAD", check=False)
        if head:
            name = head.strip().split("/", 1)[-1]
            if git("rev-parse", "--verify", "--quiet", name, check=False):
                return name
        for name in ("main", "master", "trunk", "develop"):
            if git("rev-parse", "--verify", "--quiet", name, check=False):
                return name
        return "HEAD"


# ---------- brain files ----------

def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def parse_frontmatter(text):
    """Tiny YAML subset: `key: value`, `key: [a, b]`, and `- item` lists."""
    meta, body = {}, text
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return meta, body
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return meta, body
    key = None
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = re.match(r"^\s*-\s+(.*)$", line)
        if m and key:
            if not isinstance(meta.get(key), list):
                meta[key] = []
            meta[key].append(clean(m.group(1)))
            continue
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if not m:
            continue
        key, val = m.group(1), re.sub(r"\s+#.*$", "", m.group(2)).strip()
        if val.startswith("[") and val.endswith("]"):
            meta[key] = [clean(x) for x in val[1:-1].split(",") if x.strip()]
        else:
            meta[key] = clean(val)
    return meta, "\n".join(lines[end + 1:]).lstrip("\n")


def clean(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        v = v[1:-1]
    return v


def as_list(v):
    if v is None or v == "":
        return []
    return v if isinstance(v, list) else [v]


def load_entries(repo):
    out = []
    if not os.path.isdir(repo.decisions):
        return out
    for name in sorted(os.listdir(repo.decisions)):
        if not name.endswith(".md"):
            continue
        path = os.path.join(repo.decisions, name)
        meta, body = parse_frontmatter(read(path))
        m = re.search(r"^#\s+(.+)$", body, re.M)
        title = m.group(1).strip() if m else name[:-3]
        date = str(meta.get("date") or name[:10])
        out.append({
            "id": name[:-3], "file": "brain/decisions/" + name, "name": name,
            "meta": meta, "body": body, "title": title, "date": date,
            "area": str(meta.get("area") or "general"),
            "author": str(meta.get("author") or ""),
            "commits": [c.lower() for c in as_list(meta.get("commits")) if SHA_RE.match(c.lower())],
            "source": str(meta.get("source") or "session"),
            "status": str(meta.get("status") or "active"),
            "pr": str(meta.get("pr") or ""),
        })
    return out


def load_ledger(repo):
    """Rows keyed by sha; the first row seen for a sha wins (files sorted)."""
    rows, seen = [], set()
    if not os.path.isdir(repo.ledger):
        return rows
    for name in sorted(os.listdir(repo.ledger)):
        if not name.endswith(".md"):
            continue
        for line in read(os.path.join(repo.ledger, name)).splitlines():
            if not line.startswith("|"):
                continue
            cells = [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
            sha = cells[0].strip("`").lower() if cells else ""
            if not SHA_RE.match(sha) or sha in seen:
                continue
            seen.add(sha)
            cells += [""] * (6 - len(cells))
            rows.append({"sha": sha, "date": cells[1], "author": cells[2], "area": cells[3],
                         "what": cells[4], "kind": cells[5], "file": "brain/ledger/" + name})
    return rows


def covered_prefixes(repo):
    pref = set()
    for e in load_entries(repo):
        pref.update(e["commits"])
    pref.update(r["sha"] for r in load_ledger(repo))
    return pref


def is_covered(full, prefixes, lengths):
    return any(full[:n] in prefixes for n in lengths)


# ---------- commits ----------

def read_commits(rev_args):
    fmt = "%x1e%H%x1f%P%x1f%an%x1f%ad%x1f%s%x1f%b%x1f"
    out = git("log", "--reverse", "--topo-order", "--date=short", "--numstat", "--format=" + fmt, *rev_args)
    commits = []
    for chunk in out.split("\x1e")[1:]:
        parts = chunk.split("\x1f")
        if len(parts) < 7:
            continue
        files = []
        for line in parts[6].splitlines():
            cols = line.split("\t")
            if len(cols) == 3:
                files.append((cols[2], cols[0], cols[1]))
        c = {"sha": parts[0], "parents": parts[1].split(), "author": parts[2], "date": parts[3],
             "subject": parts[4].strip(), "body": parts[5].strip(), "files": files}
        c["pr"] = next((m.group(1) for m in (r.search(c["subject"]) for r in PR_RE) if m), "")
        c["auto"], c["hint"] = classify(c)
        commits.append(c)
    return commits


def in_brain(path):
    return path.startswith("brain/") or " => brain/" in path or "{brain" in path


def classify(c):
    """-> (auto_reason or '', suggested mechanical kind or '')."""
    paths = [f[0] for f in c["files"]]
    if len(c["parents"]) > 1:
        return "merge", ""
    if paths and all(in_brain(p) for p in paths):
        return "brain-only", ""
    if paths and all(os.path.basename(p) in LOCKFILES for p in paths):
        return "", "lockfile"
    if c["subject"].lower().startswith("revert"):
        return "", ""
    if paths and all(p.lower().endswith(DOC_EXT) for p in paths):
        return "", "docs"
    for rx, kind in MECH_SUBJECT:
        if rx.search(c["subject"]):
            return "", kind
    return "", ""


def merge_groups(rev_args):
    """Map commit sha -> (merge sha, pr) for commits brought in by a merge."""
    owner = {}
    out = git("log", "--first-parent", "--merges", "--format=%H\x1f%P\x1f%s", *rev_args)
    for line in out.splitlines():
        sha, parents, subject = (line.split("\x1f") + ["", ""])[:3]
        ps = parents.split()
        if len(ps) < 2:
            continue
        pr = next((m.group(1) for m in (r.search(subject) for r in PR_RE) if m), "")
        inner = git("rev-list", ps[0] + ".." + ps[1], check=False) or ""
        for s in inner.split():
            owner.setdefault(s, (sha, pr))
    return owner


def rev_args_for(repo, a):
    branch = repo.branch(getattr(a, "branch", None))
    extra = []
    if getattr(a, "since", None):
        extra.append("--since=" + a.since)
    if getattr(a, "last", None):
        extra.append("-n%d" % a.last)
    rng = getattr(a, "range", None)
    if rng:
        revs = [rng]
    elif getattr(a, "all", False) or extra:
        revs = [branch]
    else:
        base = repo.cfg.get("baseline")
        if not base:
            die("no baseline. Run `brain.py init`, or pass --range A..B, --since DATE, --last N or --all.")
        if git("cat-file", "-e", base + "^{commit}", check=False) is None:
            die("baseline %s is not in this clone (shallow clone? rewritten history?). "
                "Fetch full history or re-run `brain.py init --baseline <sha>`." % base[:10])
        revs = [base + ".." + branch]
    args = extra + revs
    if getattr(a, "path", None):
        args += ["--"] + a.path
    return args


def uncovered(repo, a):
    args = rev_args_for(repo, a)
    commits = read_commits(args)
    pref = covered_prefixes(repo)
    lengths = sorted({len(p) for p in pref})
    auto = {}
    todo = []
    for c in commits:
        if c["auto"]:
            auto[c["auto"]] = auto.get(c["auto"], 0) + 1
        elif not is_covered(c["sha"], pref, lengths):
            todo.append(c)
    return todo, len(commits), auto, args


# ---------- commands ----------

def cmd_init(repo, a):
    branch = repo.branch(a.branch)
    base = git("rev-parse", a.baseline or branch).strip()
    if repo.cfg.get("baseline") and not a.force:
        die("brain/brain.json already has baseline %s (use --force to replace)" % repo.cfg["baseline"][:10])
    cfg = {"mode": "team", "branch": branch, "baseline": base, "tools": VERSION}
    write(repo.cfg_path, json.dumps(cfg, indent=2) + "\n")
    for d in (repo.decisions, repo.ledger):
        os.makedirs(d, exist_ok=True)
        keep = os.path.join(d, ".gitkeep")
        if not os.listdir(d):
            write(keep, "")
    ensure_ignore(repo)
    total =git("rev-list", "--count", base).strip()
    print("team brain initialised: branch %s, baseline %s" % (branch, base[:10]))
    print("%s commits exist before the baseline (not tracked unless you backfill)" % total)


def ensure_ignore(repo):
    """The index is a build output: keep it out of git so it can never conflict."""
    path = os.path.join(repo.brain, ".gitignore")
    lines = read(path).splitlines() if os.path.exists(path) else []
    if INDEX_NAME not in lines:
        write(path, "\n".join(lines + [INDEX_NAME]) + "\n")


def cmd_pending(repo, a):
    todo, scanned, auto, _ = uncovered(repo, a)
    if a.count:
        print(len(todo))
        return
    if a.json:
        print(json.dumps([{k: c[k] for k in ("sha", "author", "date", "subject", "body", "pr", "hint", "files")}
                          for c in todo[:a.limit or None]], indent=1))
        return
    owner = merge_groups(rev_args_for(repo, a)) if todo else {}
    autos = ", ".join("%d %s" % (n, k) for k, n in sorted(auto.items())) or "none"
    shown = todo[:a.limit] if a.limit else todo
    print("%d uncovered of %d commits scanned (auto-covered: %s)" % (len(todo), scanned, autos))
    if len(shown) < len(todo):
        print("showing the oldest %d; rerun after recording them for the next batch" % len(shown))
    hinted = sum(1 for c in todo if c["hint"])
    if hinted:
        print("%d look mechanical; `brain.py ledger auto` records those without reading them" % hinted)
    last_group = object()
    for c in shown:
        m = owner.get(c["sha"])
        pr = c["pr"] or (m[1] if m else "")
        group = ("PR #" + pr) if pr else (("merge " + m[0][:7]) if m else "direct")
        if group != last_group:
            print("\n== " + group)
            last_group = group
        tag = "  [mechanical? %s]" % c["hint"] if c["hint"] else ""
        print("%s %s  %s  %s%s" % (c["sha"][:7], c["date"], c["author"], c["subject"], tag))
        body = [l for l in c["body"].splitlines() if l.strip()]
        for l in body[:a.body_lines]:
            print("    | " + l.rstrip())
        if len(body) > a.body_lines:
            print("    | … (%d more lines)" % (len(body) - a.body_lines))
        for path, add, rem in c["files"][:a.files]:
            print("    %s  +%s -%s" % (path, add, rem))
        if len(c["files"]) > a.files:
            print("    … %d more files" % (len(c["files"]) - a.files))


def handle(a):
    if a.handle:
        raw = a.handle
    else:
        raw = (git("config", "user.email", check=False) or "").strip().split("@")[0] \
            or (git("config", "user.name", check=False) or "").strip() or "unknown"
    return re.sub(r"[^a-z0-9]+", "-", raw.lower()).strip("-") or "unknown"


def cell(s):
    return re.sub(r"\s+", " ", str(s)).replace("|", "\\|").strip()


def append_rows(repo, a, rows):
    who = handle(a)
    by_file = {}
    for r in rows:
        by_file.setdefault(os.path.join(repo.ledger, "%s.%s.md" % (r["date"][:7], who)), []).append(r)
    for path, rs in sorted(by_file.items()):
        if os.path.exists(path):
            text = read(path).rstrip("\n") + "\n"
        else:
            month = os.path.basename(path)[:7]
            text = ("# Commit ledger — %s (recorded by %s)\n\n"
                    "> Commits that need no decision entry. One row per commit; append with\n"
                    "> `brain.py ledger add` / `ledger auto`. kind: mechanical · minor.\n\n"
                    "| sha | date | author | area | what | kind |\n|---|---|---|---|---|---|\n") % (month, who)
        for r in rs:
            text += "| %s | %s | %s | %s | %s | %s |\n" % (
                r["sha"][:10], r["date"], cell(r["author"]), cell(r["area"]), cell(r["what"]), cell(r["kind"]))
        write(path, text)
        print("%d row(s) -> brain/ledger/%s" % (len(rs), os.path.basename(path)))


def cmd_ledger(repo, a):
    pref = covered_prefixes(repo)
    lengths = sorted({len(p) for p in pref})
    if a.action == "auto":
        todo, _, _, _ = uncovered(repo, a)
        rows = [{"sha": c["sha"], "date": c["date"], "author": c["author"], "area": c["hint"],
                 "what": c["subject"], "kind": "mechanical"} for c in todo if c["hint"]]
        if not rows:
            print("nothing to auto-record")
            return
        append_rows(repo, a, rows)
        return
    if not a.shas:
        die("ledger add needs at least one sha")
    rows = []
    for s in a.shas:
        full = git("rev-parse", "--verify", "--quiet", s + "^{commit}", check=False)
        if not full:
            die("unknown commit: " + s)
        full = full.strip()
        if is_covered(full, pref, lengths):
            print("%s already covered, skipped" % full[:7])
            continue
        info = git("show", "-s", "--date=short", "--format=%an\x1f%ad\x1f%s", full).strip().split("\x1f")
        rows.append({"sha": full, "date": info[1], "author": info[0], "area": a.area or "general",
                     "what": a.what or info[2], "kind": a.kind})
    if rows:
        append_rows(repo, a, rows)


def parse_flow(repo):
    path = os.path.join(repo.brain, "flow.md")
    if not os.path.exists(path):
        die("brain/flow.md not found")
    flows, layers, keyfiles = [], [], []
    cur, block, section = None, None, ""
    for line in read(path).splitlines():
        if line.startswith("```"):
            block = None if block else (line[3:].strip() or "text")
            continue
        if block is None:
            m = re.match(r"^##\s+(.*)$", line)
            if m:
                section = m.group(1).strip()
                fm = re.match(r"^Flow:\s*(.+?)\s*(?:\{#([\w-]+)\})?\s*$", section)
                cur = {"name": fm.group(1), "id": fm.group(2) or "", "paths": set()} if fm else None
                if cur:
                    flows.append(cur)
            elif section.lower().startswith("key files") and line.startswith("|"):
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                paths = re.findall(r"`([^`]+)`", cells[-1]) if len(cells) > 1 else []
                if paths:
                    keyfiles.append((cells[0], paths))
            continue
        if block == "layers":
            m = re.match(r"^\s*([^:#]+?)\s*:\s*(.+)$", line)
            if m:
                for p in m.group(2).split("#")[0].split(","):
                    if p.strip():
                        layers.append((p.strip().rstrip("/"), m.group(1).strip()))
        elif block == "flow" and cur is not None:
            m = re.match(r"^\s*(?:~\s*)?(?:\[[^\]]*\]\s*)?(\S+)\s+::", line)
            if m and not line.lstrip().startswith(("|", "==", "#")):
                cur["paths"].add(m.group(1))
    return flows, layers, keyfiles


def changed_files(repo, a):
    if a.range:
        spec = a.range
        if ".." in spec:
            out = git("diff", "--name-status", "-M", spec)
        else:
            out = git("show", "--name-status", "-M", "--format=", spec)
        chunks = [out]
    else:
        todo, _, _, _ = uncovered(repo, a)
        chunks = [git("show", "--name-status", "-M", "--format=", c["sha"]) for c in todo]
    status = {}
    for out in chunks:
        for line in out.splitlines():
            cols = line.split("\t")
            if len(cols) < 2:
                continue
            code = cols[0][0]
            if code == "R" and len(cols) == 3:
                status[cols[1]] = "R -> " + cols[2]
                status.setdefault(cols[2], "A")
            else:
                status[cols[1]] = {"A": "A", "D": "D", "M": "M"}.get(code, code) \
                    if status.get(cols[1]) != "A" or code == "D" else "A"
    return {p: s for p, s in status.items() if not in_brain(p)}


def cmd_impact(repo, a):
    flows, layers, keyfiles = parse_flow(repo)
    changed = changed_files(repo, a)
    if not changed:
        print("no changed files outside brain/")
        return
    traced = set()
    print("flows to re-trace:")
    hit = False
    for f in flows:
        hits = sorted(p for p in f["paths"] if p in changed)
        if hits:
            hit = True
            traced.update(hits)
            print("  %s%s" % (f["name"], "  {#%s}" % f["id"] if f["id"] else ""))
            for p in hits:
                print("    %-2s %s" % (changed[p][:1], p) + ("   (%s)" % changed[p] if changed[p].startswith("R") else ""))
    if not hit:
        print("  (none of the changed files appear in a flow block)")
    stale_rows = [(c, [p for p in ps if changed.get(p, "")[:1] in ("D", "R")]) for c, ps in keyfiles]
    stale_rows = [(c, ps) for c, ps in stale_rows if ps]
    if stale_rows:
        print("\nKey files rows naming deleted/renamed paths:")
        for c, ps in stale_rows:
            print("  %s: %s" % (c, ", ".join(ps)))
    rest = sorted(p for p in changed if p not in traced)
    if rest:
        groups = {}
        for p in rest:
            best = max((pl for pl in layers if p == pl[0] or p.startswith(pl[0] + "/")),
                       key=lambda pl: len(pl[0]), default=None)
            groups.setdefault(best[1] if best else "(no layer)", []).append(p)
        print("\nchanged but not in any flow (new entry points or calls may need tracing):")
        for layer in sorted(groups):
            print("  %s" % layer)
            for p in groups[layer][:a.files]:
                print("    %-2s %s" % (changed[p][:1], p))
            if len(groups[layer]) > a.files:
                print("    … %d more" % (len(groups[layer]) - a.files))


def cmd_index(repo, a):
    entries = load_entries(repo)
    ledger = load_ledger(repo)
    out = ["# Decisions index", "",
           "> **Generated by `python brain/tools/brain.py index`. Do not edit or commit it**",
           "> (it is git-ignored). Entries live in `brain/decisions/`, one file each.", "",
           "%d decision entries · %d ledger rows (commits needing no entry, in `brain/ledger/`)."
           % (len(entries), len(ledger)), ""]
    areas = {}
    for e in entries:
        areas.setdefault(e["area"], []).append(e)
    for area in sorted(areas, key=str.lower):
        out += ["## " + area, "", "| Date | Decision | Author | Commits | Source |", "|---|---|---|---|---|"]
        for e in sorted(areas[area], key=lambda e: (e["date"], e["name"]), reverse=True):
            title = cell(e["title"])
            if e["status"] != "active":
                title = "~~%s~~ (%s)" % (title, cell(e["status"]))
            commits = " ".join("`%s`" % c[:7] for c in e["commits"]) or "—"
            if e["pr"]:
                commits += " · #%s" % e["pr"]
            out.append("| %s | [%s](decisions/%s) | %s | %s | %s |"
                       % (e["date"], title, e["name"], cell(e["author"]) or "—", commits, e["source"]))
        out.append("")
    text = "\n".join(out).rstrip("\n") + "\n"
    ensure_ignore(repo)
    write(os.path.join(repo.brain, INDEX_NAME), text)
    print("brain/%s: %d entries in %d areas" % (INDEX_NAME, len(entries), len(areas)))
    claimed = {}
    for e in entries:
        if e["source"] in ("inferred", "backfill"):
            for c in e["commits"]:
                claimed.setdefault(c[:7], []).append(e["file"])
    for sha, files in sorted(claimed.items()):
        if len(files) > 1:
            print("possible duplicate: %s is explained by %s" % (sha, " and ".join(files)))


def cmd_find(repo, a):
    entries = load_entries(repo)
    touching = None
    if a.path:
        out = git("log", "--format=%H", repo.branch(a.branch), "--", a.path, check=False) or ""
        touching = out.split()
    hits = []
    for e in entries:
        if a.area and a.area.lower() != e["area"].lower():
            continue
        if a.author and a.author.lower() not in e["author"].lower():
            continue
        if a.source and a.source != e["source"]:
            continue
        if a.sha and not any(c.startswith(a.sha.lower()) or a.sha.lower().startswith(c) for c in e["commits"]):
            continue
        if a.text and a.text.lower() not in (e["title"] + "\n" + e["body"]).lower():
            continue
        if a.path and a.path not in e["body"] and not any(t.startswith(c) for c in e["commits"] for t in touching):
            continue
        hits.append(e)
    for e in sorted(hits, key=lambda e: (e["date"], e["name"]), reverse=True):
        flag = "" if e["status"] == "active" else "  [%s]" % e["status"]
        print("%s  %s  [%s] %s%s" % (e["date"], e["file"], e["area"], e["title"], flag))
    rows = []
    if a.sha or a.author or a.text:
        for r in load_ledger(repo):
            if a.sha and not (r["sha"].startswith(a.sha.lower()) or a.sha.lower().startswith(r["sha"])):
                continue
            if a.author and a.author.lower() not in r["author"].lower():
                continue
            if a.text and a.text.lower() not in r["what"].lower():
                continue
            if a.area and a.area.lower() != r["area"].lower():
                continue
            rows.append(r)
        for r in rows:
            print("%s  %s  ledger[%s] %s — %s (%s)" % (r["date"], r["file"], r["kind"], r["sha"][:7], r["what"], r["author"]))
    if not hits and not rows:
        print("no matches")


def slugify(s):
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return (s[:60].rstrip("-")) or "entry"


def cmd_migrate(repo, a):
    src = os.path.join(repo.brain, "decisions.md")
    if not os.path.exists(src):
        die("brain/decisions.md not found")
    text = read(src)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    head = re.compile(r"^## (\d{4}-\d{2}-\d{2})\s*[—–-]+\s*(.+?)\s*$", re.M)
    marks = list(head.finditer(text))
    if not marks:
        print("no dated entries found; nothing to split")
    author = a.author or (git("config", "user.name", check=False) or "").strip() or "unknown"
    used = set(os.listdir(repo.decisions)) if os.path.isdir(repo.decisions) else set()
    written = 0
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        body = re.sub(r"\n-{3,}\s*$", "", text[m.end():end].strip()).strip()
        date, title = m.group(1), m.group(2)
        name, n = "%s-%s.md" % (date, slugify(title)), 2
        while name in used:
            name, n = "%s-%s-%d.md" % (date, slugify(title), n), n + 1
        used.add(name)
        fm = "---\ndate: %s\nauthor: %s\narea: %s\ncommits: []\nsource: session\nstatus: active\n---\n\n" \
             % (date, author, a.area)
        write(os.path.join(repo.decisions, name), fm + "# %s\n\n%s\n" % (title, body))
        written += 1
    backup = os.path.join(repo.brain, "decisions.solo.md")
    if os.path.exists(backup):
        die("brain/decisions.solo.md already exists; entries written, original left in place")
    os.replace(src, backup)
    print("%d of %d entries written to brain/decisions/; original kept as brain/decisions.solo.md"
          % (written, len(marks)))
    cmd_index(repo, a)


def main():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(prog="brain.py", description=__doc__.split("\n\n")[0])
    ap.add_argument("--version", action="version", version=str(VERSION))
    sub = ap.add_subparsers(dest="cmd")

    def scope(p):
        p.add_argument("--branch", help="main branch (default: brain.json, else origin HEAD, main, master)")
        p.add_argument("--range", help="explicit revision range, e.g. v1.0..main")
        p.add_argument("--since", help="only commits after this date (YYYY-MM-DD)")
        p.add_argument("--last", type=int, help="only the newest N commits")
        p.add_argument("--all", action="store_true", help="whole history, ignoring the baseline")
        p.add_argument("--path", action="append", help="limit to commits touching this path (repeatable)")

    p = sub.add_parser("init", help="record baseline + branch in brain/brain.json")
    p.add_argument("--branch")
    p.add_argument("--baseline", help="commit to start tracking after (default: tip of the main branch)")
    p.add_argument("--force", action="store_true")

    p = sub.add_parser("pending", help="uncovered commits, as a digest")
    scope(p)
    p.add_argument("--count", action="store_true", help="print only the number")
    p.add_argument("--json", action="store_true")
    p.add_argument("--limit", type=int, default=40, help="max commits to print (0 = all)")
    p.add_argument("--files", type=int, default=10, help="max files listed per commit")
    p.add_argument("--body-lines", type=int, default=12)

    p = sub.add_parser("ledger", help="record commits that need no decision entry")
    p.add_argument("action", choices=["add", "auto"])
    p.add_argument("shas", nargs="*")
    p.add_argument("--area")
    p.add_argument("--what", help="one-line description (default: the commit subject)")
    p.add_argument("--kind", default="minor", choices=["minor", "mechanical"])
    p.add_argument("--handle", help="your shard name (default: from git user.email)")
    scope(p)

    p = sub.add_parser("impact", help="flows in flow.md touched by changed files")
    p.add_argument("range", nargs="?", help="A..B or a single sha (default: all uncovered commits)")
    p.add_argument("--files", type=int, default=15)
    p.add_argument("--branch")

    p = sub.add_parser("index", help="regenerate brain/decisions-index.md (git-ignored)")

    p = sub.add_parser("find", help="look up entries and ledger rows")
    for flag in ("--area", "--author", "--sha", "--path", "--text", "--source", "--branch"):
        p.add_argument(flag)

    p = sub.add_parser("migrate", help="split a solo decisions.md into brain/decisions/")
    p.add_argument("--author", help="author recorded on migrated entries (default: git user.name)")
    p.add_argument("--area", default="general")

    a = ap.parse_args()
    if not a.cmd:
        ap.print_help()
        return
    repo = Repo()
    if a.cmd != "init" and not os.path.isdir(repo.brain):
        die("no brain/ folder in " + repo.root)
    {"init": cmd_init, "pending": cmd_pending, "ledger": cmd_ledger, "impact": cmd_impact,
     "index": cmd_index, "find": cmd_find, "migrate": cmd_migrate}[a.cmd](repo, a)


if __name__ == "__main__":
    main()
