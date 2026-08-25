# Execution Flow — Whole System

> **Maintenance:** when a change alters how execution travels, update the
> relevant call-tree, the Key-files table, and the end-to-end trace; tag
> edits inline with `[CHANGED: <area>]`. Keep it whole-system, every session.

How execution actually travels through this project: what calls what, in what
order, across files, modules, and process boundaries. Covers the entire
codebase, not just recent edits — recent work is tagged inline with
`[CHANGED: <area>]` (the *rationale* for those changes lives in
`decisions.md`).

---

## 0. The big picture

<!-- One diagram or short paragraph: the major components and how they talk.
     ASCII boxes work well:

     Client ──▶ API Gateway ──▶ Service A ──▶ Database
                     └────────▶ Service B ──▶ External API
-->

---

## 1. <Primary flow name — e.g. "Request handling", "Main pipeline">

<!-- An indented call tree, annotated. Example shape:

```
src/server.ts :: main()
  ├─ loadConfig()            (src/config.ts — env + defaults)
  ├─ createApp()
  │    ├─ registerMiddleware()   auth → rate-limit → logging
  │    └─ registerRoutes()       → src/routes/*.ts
  └─ listen(PORT)
```

Add one numbered section per distinct flow (startup, request path, background
jobs, data sync, frontend data path, …). -->

---

## Key files quick-reference

| Concern | File |
|---|---|
| <!-- e.g. Entry point --> | <!-- e.g. `src/server.ts` --> |

---

## End-to-end trace

<!-- The single most important user action, traced start to finish in one
     compact block:

```
User clicks X → frontend calls POST /api/y → handler validates →
service does Z → DB write → response → UI updates
```
-->
