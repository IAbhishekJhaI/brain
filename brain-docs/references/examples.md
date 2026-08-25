# Worked examples — what good entries look like

These examples come from a real project (names generalized). Use them to
calibrate depth and tone: specific enough that a future session can act on
them, short enough that they actually get written.

---

## 1. A `decisions.md` entry

Note what makes this work: the **D** names the exact files and seams; the
**A** stops a future session from re-proposing the rejected option; the **T**
is honest about what got worse; **Verified** records the proof.

````markdown
## 2026-08-21 — Routing: Google Routes API → Mapbox (Matrix + Directions)

- **D:** Replaced `GoogleRoutesAdapter` with `MapboxRoutesAdapter` (same file
  `integrations/routes.py`, same public methods `get_duration_matrix` /
  `get_leg_options`, same return types). The duration matrix now hits the
  Mapbox Matrix API and per-leg directions the Mapbox Directions API. Places
  search stays Google — only routing moved. Cache namespace bumped
  `route_matrix` → `route_matrix_mb` so stale entries aren't served.
- **W:** Consolidate on the Mapbox stack the map UI already uses; simpler
  billing. The provider protocol is narrow, so the swap is drop-in — the
  pipeline and all fake-provider tests are unchanged.
- **A:** Rejected keeping Google Routes as a config-selectable fallback —
  more wiring to maintain for a clean cutover. Rejected the live-traffic
  matrix (caps at 10 coordinates; a day can need 23 → would need several
  stitched calls).
- **T:** The matrix loses live traffic (typical/historical only). Accepted:
  the old code added no traffic buffer anyway, so real-world impact is
  small. Gotcha baked into a test: Mapbox coordinates are `lng,lat` —
  opposite of Google.
- **Verified:** full backend suite green; `check_providers.py` probes the
  new Matrix endpoint.
````

A trivial edit — renaming a variable, bumping a dependency patch version,
fixing a typo — gets **no entry**. The bar: would a future maintainer ask
"why?".

---

## 2. A `flow.md` call-tree section (with `[CHANGED]` tags)

The tree shows *what calls what*, annotated with what each hop does. The
`[CHANGED: auth]` tags mark where a piece of work touched the flow — a reader
can grep the tag to see that work's whole footprint. The doc always describes
the **current** system; the tags are breadcrumbs, not a changelog.

````markdown
## 3. Auth: verify → resolve → provision

Applies to any endpoint depending on `get_current_user_id`.

```
FRONTEND token attachment
  src/app/layout.tsx
    └─ <AuthProvider>            [CHANGED: auth]
         └─ <AuthTokenBridge/>   getToken → api.setAuthTokenGetter
  src/lib/api.ts :: request()    [CHANGED: auth] await tokenGetter()
                                 → Bearer header (guest → none)

BACKEND
  app/api/deps.py :: get_current_user_id(db, authorization)
    ├─ no header   → None (guest)
    ├─ bad scheme  → 401
    ├─ claims = verify_token(token)     # core/auth.py [NEW]
    │     JWKS cache → jwt.decode(RS256, issuer, exp/nbf)
    └─ get_or_create_user(db, claims):
         SELECT user WHERE external_id == sub ; else INSERT ; commit
         → internal user id (UUID)
```
````

And the Key-files table row that goes with it:

```markdown
| Concern | File |
|---|---|
| Auth | `app/api/deps.py`, `app/core/auth.py` [NEW] |
```

---

## 3. `todo.md` entries

Each item: severity tag, provenance, what/why/where, and a file ref. Note the
🟡 item — it records something *deliberate* so a future session doesn't
"fix" it.

```markdown
## 🔴 Action required

- [ ] **Set `MAPBOX_ACCESS_TOKEN` in prod env** `(session)` — routing now
  uses Mapbox; local `.env` has the token but prod doesn't, so every plan's
  route matrix fails there. Needs Directions + Matrix APIs enabled. Verify
  with `python scripts/check_providers.py`. `integrations/routes.py`.

## 🟠 Correctness / security observations

- [ ] **Rate limiter likely keys on the proxy IP, not the client.**
  `(session)` `rate_limit.py` uses `request.client.host`, but the deploy has
  no `--proxy-headers`, so behind the proxy every request may share one IP →
  the per-IP limit becomes effectively global. Verify the deployed value;
  honor `X-Forwarded-For` if it's the proxy. `rate_limit.py:19`.

## 🟡 Known limitations (by design)

- [ ] **The route matrix uses typical traffic, not live.** `(session)` The
  live-traffic API caps at 10 coordinates; a full day needs more, so the
  whole-plan matrix uses the historical profile. Per-leg calls could switch
  to live later if ETAs matter. `integrations/routes.py::get_duration_matrix`.

## 🔵 Tech debt / cleanups

- [ ] **Delete dead HS256 scaffold** `(session)` — `core/security.py` is
  unused since the auth migration. Remove with its deps if nothing else
  needs them.
```

When the token item above gets done, it becomes `- [x]` (or is removed), and
if resolving it involved a real choice, that choice gets a `decisions.md`
entry the same day.
