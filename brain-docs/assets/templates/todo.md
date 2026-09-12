# TODO / Notes

> **Maintenance:** add caveats/risks/ideas as they surface. Organize **by
> topic, not by date** — group items under functional-area headings, tag each
> with its severity emoji, and **never** add dated session sub-headings (put
> the date in the item's `(session …)` tag). When an item is done, check it
> `[x]` and move it to `brain/archive.md` (same topic sections).

Things worth noting: action items, caveats, correctness/security
observations, and feature ideas that surfaced while working.

Tags: 🔴 action-required · 🟠 correctness/security · 🟡 known limitation
(by design) · 🟢 feature · 🔵 tech-debt. `(session)` = surfaced while
working · `(roadmap)` = imported from a plan/handoff doc.

A short list can stay flat. Once it grows, split it into **topic sections**
like the examples below — the severity emoji rides on each item as a tag, so
you can still scan "all the 🔴s" by eye while keeping related work together.
Completed items live in `brain/archive.md`.

---

## Deploy & ops

<!-- Blocking config/infra: keys, migrations, env, one-off scripts.
- [ ] 🔴 **Short imperative title.** `(session)` — what, why it blocks, exact
      command or step to resolve. `path/to/file.py:123`.
-->

## Backend / API

<!-- Correctness, limitations, and ideas in the server/engine/data layer.
- [ ] 🟠 **What's wrong.** `(session)` — the failure scenario, where it lives,
      and the sketch of a fix. `path/to/service.py:45`.
- [ ] 🟡 **A deliberate limitation.** `(session)` — why it's acceptable today,
      and what would trigger revisiting it. `path/to/module.py`.
-->

## Frontend / UI

<!-- Client-side items.
- [ ] 🟢 **The idea.** `(session)` — the value, and a sketch of the seams it
      would touch. `path/to/Component.tsx`.
-->

## Tech debt / cleanups

<!-- Non-urgent cleanups, any layer.
- [ ] 🔵 **The cleanup.** `(session)` — what and where. `path/to/file.ts`.
-->

<!-- Add / rename topic sections to fit the project (Auth, Payments,
     Infra, …). The set above is just a starting point. -->
