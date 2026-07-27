---
idea: IDEA-006
doc: 02_ARCHITECTURE
version: 0.2.0
standard: GUILD-DOC-STANDARD@0.2.0
status: active
updated: 2026-07-24
note: ARCH-PASS (MSN-004 P4, cash lane). Original 0.1.0 content (2026-07-18) re-verified accurate,
  not rewritten — see the appended addendum below for E0/E1/E2.
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

---

## ARCH-PASS addendum (2026-07-24, MSN-004 P4, cash lane)

> Per `docs/methodology/ARCH_PASS.md` — E0 requirements snapshot with real measures, E1 honest AS-IS
> (verified by reading files, not by trusting prior docs), E2 target + gap list. Appended, not a
> rewrite — the sections above (written 2026-07-18, MSN-002 squad A) were re-verified this pass and
> found accurate; nothing above needed correcting.

### E0 — Requirements snapshot

**What this app must do:** be the public conversion surface for the Pack Fábrica de Agentes offer —
capture leads at `/gratis/`, sell at `/`, hand off cleanly to Hotmart checkout and back to
`/obrigado/` — at effectively $0 hosting cost, with search engines and social shares seeing correct
canonical metadata.

**Quality-attribute scenarios (measured this pass):**
1. **Zero build-step deploy stays true.** Measured: no `package.json`, `next.config.*`, or any
   framework manifest found in the repo root or subtree (`find` on the repo turned up only `.html`,
   `.css`, `.js`, `.py`, `.xml`, `.txt`, `CNAME`) — confirms the mission brief's "Next.js" description
   does not match this repo; it is plain static HTML/CSS/JS as `02_ARCHITECTURE.md` already stated.
   Corrected in this repo's own `CLAUDE.md`/`AGENTS.md` (new, this pass) so the mismatch isn't
   repeated.
2. **Checkout CTAs are live, not placeholder.** Measured: read `index.html` directly —
   `#cta-hero`/`#cta-comprar` both resolve to `pay.hotmart.com/C106375857V` with distinct `sck` UTM
   tags, JSON-LD `availability` is `InStock`. Matches `06_OPERATIONS.md`'s "done" claim exactly.
3. **SEO canonicalization is internally consistent.** Measured: `rel=canonical`/`og:url` on
   `index.html` (`https://fabricadeagentes.caiocastilho.com/`) now matches `robots.txt`'s `Sitemap:`
   line and every URL in `sitemap.xml` — the mismatch flagged in `05_MARKETING.md` was fixed in the
   prior commit on this branch (`ccb00df`, this same session); re-verified true by reading all three
   files fresh.
4. **All three HTML pages parse cleanly.** Measured: `index.html`, `gratis/index.html`,
   `obrigado/index.html` fed through Python's stdlib `html.parser` this pass — no parse errors on any
   of the three.
5. **Lead-capture form posts to the documented Brevo endpoint.** Measured: `gratis/index.html`'s
   `#brevo-form` `action=` attribute is a live `sibforms.com` URL, consistent with `02_ARCHITECTURE.md`
   §Lead capture. The HTML comment directly below it (line 61) already self-flags the real HITL gap —
   the Brevo automation only attaches the Agente 01 PDF, not all 3 — matching the cross-reference to
   `project-money/docs/qa/AGENTS_QA_REPORT.md` this doc already makes.
6. **TLS/HTTPS enforcement — ✅ now verified live (2026-07-27, MSN-020).** The earlier pass correctly
   refused to assert this: it had no authenticated `gh api`/Pages access, so it carried the
   `*.github.io`-certificate finding forward as-documented instead of claiming a fresh check. That
   discipline was right, and it is now closed with evidence — `openssl` returns
   `subject=CN=fabricadeagentes.caiocastilho.com` (Let's Encrypt, through 2026-10-23) and the Pages
   API reports `https_certificate.state=approved`, `https_enforced=true`. Fixed 2026-07-25 23:56 on
   `main`; PR #8 was closed, not merged. See `06_OPERATIONS.md` §Custom domain.

   Worth keeping as a worked example: **"not verified" aged well, "still broken" did not.** The
   sibling claim in `06_OPERATIONS.md` asserted the gap as current fact and was merged ~50 minutes
   after it had already been fixed, then stood as the authoritative status for two days.

**Constraints:** R$0 posture (DEC-001-034); marketing copy/pricing/checkout mechanics are out of
scope for this pass (documentation/infra only, per the ARCH-PASS mission's HITL-sensitivity rule for
this repo); PRs #5 and #8 are pre-existing, untouched, awaiting Caio's review.

### E1 — AS-IS confirmed

No divergence found between `02_ARCHITECTURE.md`'s existing description and the live repo state — the
2026-07-18 doc pass (MSN-002 squad A) was accurate. The one correction made *is* this addendum plus
the new quartel kit: the ARCH-PASS mission brief assumed a Next.js stack for this repo; the repo is
static HTML/CSS/JS with no framework, no build step, no `node_modules`, no test runner. `CLAUDE.md`
and `AGENTS.md` (new, this pass) state this explicitly so no future session inherits the wrong
assumption.

**Infra reality (for `INFRA_CHECKLIST.md`):**
- **Deploy target:** GitHub Pages, `main` branch root, custom domain via `CNAME`. No CD workflow — a
  commit to `main` is the deploy.
- **DB:** none — no data store in this repo. Lead data lives in Brevo (external SaaS); no export/read
  path exists from this repo.
- **CI:** none — no `.github/workflows/` found. Verification is manual: HTML parse check (this pass)
  + `python3 -m py_compile` on `automation/publish_instagram.py` (ran, clean).
- **Secrets:** none in this repo. `FB_PIXEL_ID` in `pixel.js` is a public tracking ID, not a secret
  (confirmed already documented in `06_OPERATIONS.md` §Secrets, re-verified true).
- **Costs:** R$0 fixed (GitHub Pages free tier + already-owned domain); Hotmart's fee is per-sale, not
  a hosting cost.
- **Contract:** no `.boss/app.manifest.yaml` found in this repo — this is a static marketing site, not
  a BOSS-integrated app; N/A rather than a gap (same reasoning as any pure-static Pages site in the
  portfolio).

### E2 — Target + gap list

No new target invented — this repo's own `04_ROADMAP.md` already lists the two real open items
correctly (TLS enforcement, PR #8; LP conversion audit, PR #5), both correctly left as open PRs for
Caio rather than self-merged. This pass adds nothing to that list; it confirms the list is still
accurate and complete.

**Gap list → dispatch:**
| Gap | Disposition |
|---|---|
| No CI (`.github/workflows/`) | Not fixed this pass — real scope (would need an HTML-lint/link-check workflow), better sized as its own follow-up than an ARCH-PASS side effect. Noted in `INFRA_CHECKLIST.md`. |
| Quartel kit missing at root | Fixed this pass — `CLAUDE.md` + `AGENTS.md` added. |
| Mission-brief stack description (Next.js) doesn't match repo reality (static HTML) | Corrected in the new kit; not a repo bug, a documentation-drift risk for future sessions. |
| TLS enforcement, LP conversion audit | Already tracked (PR #8, PR #5) — not duplicated here, not touched (HITL/review-gated per this repo's own rules). |

**Quartel kit:** installed this pass (`CLAUDE.md`, `AGENTS.md` at repo root).
