---
idea: IDEA-006
doc: 06_OPERATIONS
version: 0.1.0
standard: GUILD-DOC-STANDARD@0.2.0
status: active
updated: 2026-07-18
---

# fabrica-de-agentes (public site) — Operations

## Deploy

GitHub Pages serves the `main` branch root directly — no build step, no CI. Edit → commit to `main` →
live in ~1 minute (per `README.md`). There is no staging environment; PRs are the review gate before
merge to `main`.

## Custom domain

`CNAME` file pins `fabricadeagentes.caiocastilho.com`. DNS is external (not managed in this repo).
**Known gap (MSN-017, 2026-07-16): HTTPS enforcement was never turned on** for the custom domain in
the repo's Pages settings — the site currently serves a `*.github.io` certificate, which browsers flag
as a security warning for every visitor on the custom domain. Fix: GitHub repo Settings → Pages →
"Enforce HTTPS" (a ~4-click, Caio-only action per MSN-017; requires the DNS to have already propagated,
which it has since `CNAME` already resolves). Staged as PR `#8` + a revert to follow merge — Claude
cannot merge PRs in this harness.

## Checkout migration (CTA) — done

Per DEC-F1-002 (Hotmart/Gumroad decision), the LP originally shipped with a placeholder checkout
state. **Migration is complete**: `#cta-hero` and `#cta-comprar` in `index.html` both point at the
live Hotmart checkout (`pay.hotmart.com/C106375857V`, with `sck` UTM tags distinguishing the two CTA
positions), and the JSON-LD `availability` is `InStock`. No further action needed here — remaining
blockers are Hotmart *dashboard* config (thank-you page, order bump, affiliates), not this repo.

## Costs

R$0 — GitHub Pages is free; the only paid dependency is the Hotmart transaction fee (per-sale, not a
fixed cost) and the custom domain (already owned, `caiocastilho.com`).

## Secrets

None in this repo. `FB_PIXEL_ID` in `pixel.js` is a public tracking ID (not a secret) and is already
filled in. Brevo/Hotmart API keys, if any, live in those services' own dashboards, not in this repo.
