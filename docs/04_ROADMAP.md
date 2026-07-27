---
idea: IDEA-006
doc: 04_ROADMAP
version: 0.1.0
standard: GUILD-DOC-STANDARD@0.2.0
status: active
updated: 2026-07-18
---

# fabrica-de-agentes (public site) — Roadmap

Full IDEA-006 roadmap lives in `project-money/docs/04_ROADMAP.md`; this tracks only what's specific
to this repo's build.

## Done

- LP live at the custom domain, CTA anchors ready to point at checkout.
- `/gratis/` lead magnet expanded from 1 to 3 agents (DEC-F1-006).
- Meta Pixel wired and gated, ID filled in and confirmed firing (MSN-017, 2026-07-16).
- `robots.txt`/`sitemap.xml` corrected to the custom domain (were still pointing at the old
  `engineeringguild.github.io/fabrica-de-agentes/` URL — fixed 2026-07-18).
- **Custom-domain TLS/HTTPS enforcement — ✅ done 2026-07-25 23:56**, verified live 2026-07-27
  (MSN-020): Let's Encrypt cert for `CN=fabricadeagentes.caiocastilho.com`, valid through
  **2026-10-23**; Pages API reports `state=approved` and `https_enforced=true`; `curl` without `-k`
  returns 200 across the funnel. Fixed by `Delete CNAME` → `Create CNAME` on `main` via the web UI;
  **PR `#8` was closed, not merged**. Detail and the lesson learned: `06_OPERATIONS.md` §Custom domain.

## Open — this repo

- **LP conversion audit** (headline/demo/social-proof improvements) — left as an open PR by design
  (`#5`, MSN-016) since the LP is the offer's face and shouldn't be self-merged.

## Open — outside this repo (tracked here for visibility only)

Hotmart thank-you page config, order bump, affiliate program, Brevo attachment fix, beta-tester
outreach — all HITL, tracked in `project-money/docs/WAR_ROOM.md`, not actionable from this repo.
