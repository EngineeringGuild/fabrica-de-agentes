---
idea: IDEA-006
doc: 05_MARKETING
version: 0.1.0
standard: GUILD-DOC-STANDARD@0.2.0
status: active
updated: 2026-07-18
---

# fabrica-de-agentes (public site) — LP/SEO lane

Full acquisition strategy (content, affiliates, ads) lives in `project-money/docs/marketing/`. This
covers only what's encoded in this repo's files.

## Canonical URLs

Every page declares its canonical URL and OG tags pointing at the custom domain
(`https://fabricadeagentes.caiocastilho.com/...`). **`robots.txt` and `sitemap.xml` were out of sync**
with this — both still referenced the pre-custom-domain `engineeringguild.github.io/fabrica-de-agentes/`
URL, which would have confused search-engine canonicalization (sitemap URLs disagreeing with the
`rel=canonical` tags on the actual pages). **Fixed 2026-07-18**: both now point at the custom domain.

## Indexing

`robots.txt`: `Allow: /`, `Disallow: /obrigado/` (correctly keeps the post-purchase page out of the
index). `sitemap.xml` lists `/` and `/gratis/` (priority 1.0 / 0.8) — `/obrigado/` is intentionally
excluded, matching robots.txt.

## Positioning (as encoded in the LP)

R$47 launch price, JSON-LD structured data on `index.html` (flip `availability` to `InStock` once
checkout is live — see the README's own note). Lead magnet (`/gratis/`) is the funnel entry: captures
via Brevo, delivers 3 of the 10 agent PDFs.

## Next SEO actions

- Verify Google Search Console / Bing Webmaster picked up the corrected sitemap after this fix.
- Once the TLS fix (`04_ROADMAP.md`) lands, re-crawl to confirm no mixed-certificate warnings affect
  indexing or the security browser warning that currently greets every visitor.
