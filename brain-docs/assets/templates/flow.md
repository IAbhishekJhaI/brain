# Execution Flow — <Project>

> **Snapshot of the CURRENT code — not a changelog.** When code changes,
> re-trace the affected flow and replace its block. No `[CHANGED]` tags, dates,
> or "was / no longer / supersedes" wording; rationale goes in `decisions.md`.
> Notes ≤ 80 chars, flows ≤ 40 lines. View it with
> `flow-viewer.html` (same folder).

## Overview

<!-- One edge per line: `A -> B : label`  (`<->` for two-way). -->
```components
Client -> API : HTTP
API -> Service : call
Service -> Database : SQL
```

<!-- Optional: the viewer's swimlanes, left to right. `Name : path/prefix, …`
     A step lands in the layer whose prefix matches its path most specifically.
     Without this block, each top-level folder is a layer. -->
```layers
App : src
```

<!-- One or two sentences on the architecture, if the diagram needs it. -->

## Flow: <Primary flow name> {#primary}

Trigger: <what starts it — a user action, an endpoint, a cron, a CLI command>

<!-- Grammar (one call per line, 2-space indent = "calls", in source order):
       path/to/file :: symbol()  — what this hop does   ← call
       helper()                                         ← call in the parent's file
       => POST /api/thing                               ← process/network boundary
       db: INSERT orders  /  ext: Stripe charge         ← side effect (db ext cache queue fs env log)
       → 401                                            ← returns / responds with
       [if cond] … / [else] …                           ← branch
       ~ …                                              ← async / background
       @other-flow-id                                   ← continues in another flow
       … # comment                                      ← ignored by the viewer
     Optional trace extras (don't count toward the 40-line budget):
       == Phase name — short subtitle                   ← starts a phase of the trace
         | plain: one jargon-free sentence              ← under a step: shown in presentation mode
         | passes: Artefact { handed, on }              ← what this step hands to the next
         | fails: what really happens when it breaks    ← only for real degradation -->
```flow
== Boot — read the settings, start serving
src/server.ts :: main()  — boot the app
  | plain: Starts the app and gets it ready for requests.
  src/config.ts :: loadConfig()  — env + defaults
    | passes: Config { port, dbUrl }
  src/app.ts :: createApp()
    registerRoutes()  — mounts src/routes/*
  listen(PORT)
```

## Key files

| Concern | Files |
|---|---|
| Entry point | `src/server.ts` |
