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

## Open — this repo

- **Custom-domain TLS/HTTPS enforcement** — never provisioned; the site currently serves a
  `*.github.io` certificate for the custom domain, which shows a browser security warning to every
  visitor. This is a GitHub Pages repo-settings change (Enforce HTTPS checkbox, after DNS
  propagation), not a file in this repo — staged as PR `#8` (+ a revert to follow) per MSN-017. Merge
  is Caio's, not an agent's, in this harness.
- **LP conversion audit** (headline/demo/social-proof improvements) — left as an open PR by design
  (`#5`, MSN-016) since the LP is the offer's face and shouldn't be self-merged.

## Open — outside this repo (tracked here for visibility only)

Hotmart thank-you page config, order bump, affiliate program, Brevo attachment fix, beta-tester
outreach — all HITL, tracked in `project-money/docs/WAR_ROOM.md`, not actionable from this repo.
