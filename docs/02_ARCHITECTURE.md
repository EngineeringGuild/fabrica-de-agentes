---
idea: IDEA-006
doc: 02_ARCHITECTURE
version: 0.1.0
standard: GUILD-DOC-STANDARD@0.2.0
status: active
updated: 2026-07-18
---

# fabrica-de-agentes (public site) — Architecture

## Stack

Plain static HTML/CSS/JS, no build step, no framework. Served by GitHub Pages from the `main` branch
root. Custom domain via `CNAME` (`fabricadeagentes.caiocastilho.com`).

## Structure

```
/               index.html — the offer LP (R$47 launch price)
/gratis/        lead magnet — 3 of the 10 agents (01 FAQ, 02 Social Content, 04 Follow-up),
                Brevo capture form, PDFs served from /downloads/
/obrigado/      post-purchase thank-you page (configured as the Hotmart thank-you redirect)
/downloads/     public PDF assets (the 3 free-tier agent prompts)
/automation/    publish_instagram.py — a standalone script, not wired into the site build
pixel.js        Meta Pixel loader, gated on window.FB_PIXEL_ID (see below)
style.css       shared styles
robots.txt, sitemap.xml   SEO — see 05_MARKETING.md
CNAME           custom domain pointer for GitHub Pages
```

## Tracking (Meta Pixel)

`pixel.js` is a self-gating loader: it does nothing until `window.FB_PIXEL_ID` is set. The ID is
already filled in (`1012110551536514`, confirmed live per MSN-017/2026-07-16). PageView fires
automatically; `Lead`/`InitiateCheckout`/`Purchase` events fire from the relevant pages via
`window.fdaTrack(eventName, params)`, which is safe to call even if the pixel is disabled (no-op).

## Lead capture

`/gratis/` embeds a Brevo form. Delivery of the 3 PDFs is handled by a Brevo automation (not code in
this repo) — see `project-money/docs/qa/AGENTS_QA_REPORT.md` for the delivery-content history and
`project-money/docs/marketing/EMAIL_SEQUENCE_BREVO.md` for the sequence itself.

## Checkout

Hotmart-hosted checkout (external — this repo only links to it). The CTA anchors (`#cta-hero`,
`#cta-comprar`) in `index.html` point at the checkout URL once live; see `06_OPERATIONS.md` for the
migration note from the original placeholder state.
