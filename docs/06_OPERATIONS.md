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

**Status: ✅ resolved 2026-07-25 23:56** (verified live 2026-07-27, MSN-020):

```
subject=CN=fabricadeagentes.caiocastilho.com
issuer=C=US, O=Let's Encrypt, CN=YR1
notBefore=Jul 25 22:57:50 2026 GMT
notAfter=Oct 23 22:57:49 2026 GMT
```

`GET /repos/EngineeringGuild/fabrica-de-agentes/pages` → `https_certificate.state=approved`,
`https_enforced=true`. `curl` **without `-k`** returns 200 on `/`, `/gratis/`, `/obrigado/` with
`ssl_verify_result=0`; `http://` 301s to `https://`. **Certificate expires 2026-10-23** — renewal is
automatic, but a funnel-health monitor now watches the expiry date (MSN-020).

How it was actually fixed, for the record: `Delete CNAME` (`e88e55a0`, 23:56:01) followed by
`Create CNAME` (`473d1f14`, 23:56:09) straight on `main` via the GitHub web UI, which re-triggered
certificate provisioning. **PR `#8` was closed, not merged** — the staged procedure worked, but it
went around the PR flow, so nothing in the repo recorded the outcome.

> ⚠️ **Why this paragraph is worth reading twice.** The previous version of this section — claiming
> the site served a `*.github.io` cert and warned every visitor — was **merged into `main` roughly 50
> minutes AFTER the certificate was already fixed** (PR `#9`, 2026-07-26 00:46). It then sat there for
> two days as the authoritative status, which is exactly what a returning session reads first. A status
> doc written without re-checking the live target is worse than no status doc: it misdirects the next
> session's priorities. **Re-verify against the target before writing status.**

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
