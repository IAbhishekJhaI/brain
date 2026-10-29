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

## 2. A `flow.md` flow section

One `## Flow:` per entry point, a `Trigger:` line, and a ` ```flow ` block:
one call per line, indentation = "calls", short notes saying *what* each hop
does. Shared paths are their own flow, referenced with `@id` rather than
copied into every caller. Nothing in it says when or why anything changed.

````markdown
## Flow: Authenticated request {#auth}

Trigger: any API route that depends on `get_current_user_id`

```flow
web/src/lib/api.ts :: request()  — attach Bearer token if signed in
  tokenGetter()  — Clerk session token; guests send none
  => any /v1/* route
    app/api/deps.py :: get_current_user_id(db, authorization)
      [if no header] → None  — guest
      [if bad scheme] → 401
      app/core/auth.py :: verify_token(token)  — RS256 via cached JWKS
        cache: jwks
        [if cache miss] ext: Clerk JWKS endpoint
      app/services/users.py :: get_or_create_user(db, claims)
        db: SELECT users WHERE external_id = sub
        [if missing] db: INSERT users
```
````

And its Key-files row — paths only:

```markdown
| Concern | Files |
|---|---|
| Auth | `app/api/deps.py`, `app/core/auth.py`, `web/src/lib/api.ts` |
```

### Bad → good: how a flow.md rots

This node is from a real project's legacy flow.md (lightly trimmed). It is
one middleware hop that grew to 17 lines:

```
  ├─ RateLimitMiddleware   → app/core/rate_limit.py   ← INSIDE CORS
  │     [CHANGED: rate-limit] per-IDENTITY, COST-WEIGHTED two-bucket WEIGHTED
  │       SLIDING window (the old one was a fixed bucket mislabelled "sliding" —
  │       it allowed a 2x burst across the minute boundary). One atomic EVALSHA
  │       does read + decide + INCRBY + TTL, so no counter can be left immortal
  │       (the old INCR-then-EXPIRE could). Budget = RATE_LIMIT_PER_MINUTE cost
  │       units (default 240); COSTS table: POST /v1/itineraries 60, PATCH 30, …
  │       [CHANGED: cache-resilience] FAILS OPEN (allow + log) if Upstash is
  │         down — a limiter sits in front of EVERY request, so a Redis outage
  │         must not 500 the API. [CHANGED: rate-limit] the except now also
  │         covers ValueError/OSError, so a blank REDIS_URL fails open too …
```

What went wrong: change tags that never get cleared, the *old* behaviour
described next to the new, rationale ("so that…", "must not…"), and
configuration detail that belongs in code comments. The same hop, current
state only:

```flow
app/core/rate_limit.py :: RateLimitMiddleware  — cost-weighted sliding window per client IP
  cache: EVALSHA rate-limit script  — read + decide + increment, atomic
  [if Redis unavailable] log: fail open
  [if over budget] → 429 + Retry-After
```

Everything that was cut still has a home:
- **Why** sliding-window, why fail-open, why atomic Lua → `decisions.md`
  (one D/W/A/T entry each, with the rejected fixed-bucket design under **A**).
- **The cost table and default budget** → the code (`COSTS` in
  `rate_limit.py`); flow.md points at the file, it doesn't mirror config.
- **"A blank `REDIS_URL` also fails open"** → `todo.md` as a 🟡 known
  limitation if it's worth remembering.

---

## 3. `todo.md` entries

Group items under **topic** headings (not dates); each item carries its
severity emoji as an inline tag, plus provenance, what/why/where, and a file
ref. Note the 🟡 item — it records something *deliberate* so a future session
doesn't "fix" it — and how items of different severities sit together under
the topic they belong to.

```markdown
## Deploy & ops

- [ ] 🔴 **Set `MAPBOX_ACCESS_TOKEN` in prod env** `(session)` — routing now
  uses Mapbox; local `.env` has the token but prod doesn't, so every plan's
  route matrix fails there. Needs Directions + Matrix APIs enabled. Verify
  with `python scripts/check_providers.py`. `integrations/routes.py`.

## Routing & maps

- [ ] 🟡 **The route matrix uses typical traffic, not live.** `(session)` The
  live-traffic API caps at 10 coordinates; a full day needs more, so the
  whole-plan matrix uses the historical profile. Per-leg calls could switch
  to live later if ETAs matter. `integrations/routes.py::get_duration_matrix`.

## Security

- [ ] 🟠 **Rate limiter likely keys on the proxy IP, not the client.**
  `(session)` `rate_limit.py` uses `request.client.host`, but the deploy has
  no `--proxy-headers`, so behind the proxy every request may share one IP →
  the per-IP limit becomes effectively global. Verify the deployed value;
  honor `X-Forwarded-For` if it's the proxy. `rate_limit.py:19`.

## Tech debt

- [ ] 🔵 **Delete dead HS256 scaffold** `(session)` — `core/security.py` is
  unused since the auth migration. Remove with its deps if nothing else
  needs them.
```

When the token item above gets done, it becomes `- [x]` and **moves to
`brain/archive.md`** (under the same "Deploy & ops" heading) so `todo.md`
stays a list of open work. And if resolving it involved a real choice, that
choice gets a `decisions.md` entry the same day.
