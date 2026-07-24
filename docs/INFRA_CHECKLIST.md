---
idea: IDEA-006
doc: INFRA_CHECKLIST
version: 0.1.0
standard: GUILD-DOC-STANDARD@0.2.0
status: active
updated: 2026-07-24
note: ARCH-PASS (MSN-004 P4). Production-readiness contract per docs/methodology/ARCH_PASS.md.
---

# fabrica-de-agentes — Infra Checklist

| Area | Item | State | Evidence/Gap |
|---|---|---|---|
| Deploy | target per DEC-001-032 (Workers/Pages/GH-Pages) + CD workflow | ✅ | GitHub Pages, `main` branch root, custom domain via `CNAME` (`fabricadeagentes.caiocastilho.com`). No separate CD workflow needed — a commit to `main` *is* the deploy (confirmed: no `.github/workflows/` directory exists, and none is needed for this shape). |
| Deploy | rollback path (git revert + redeploy) documented | ✅ | `git revert` on `main` → live in ~1 minute per `README.md`/`06_OPERATIONS.md`. No build artifact to invalidate — static files serve directly. |
| DB | project ref + status (ACTIVE/INACTIVE) + migrations source of truth | N/A | No database in this repo. Lead data is captured by an external Brevo form (`gratis/index.html` `#brevo-form`, posts to a `sibforms.com` endpoint) — this repo has no read/export path to that data. |
| DB | RLS/isolation VERIFIED by a test (not "designed") | N/A | No data store to isolate. |
| Secrets | all by NAME in 06_OPERATIONS (build/runtime/infra scopes); repo greps clean | ✅ | `06_OPERATIONS.md` §Secrets states none in this repo; `FB_PIXEL_ID` in `pixel.js` is a public tracking ID (`1012110551536514`), not a secret. Grepped this pass for API-key-shaped strings in tracked files — none found beyond the pixel ID and the public Brevo form endpoint (both intentionally public). |
| CI | verify gates (lint/type/test/build) green on default branch | ❌ | **Real gap.** No `.github/workflows/` in this repo — no HTML lint, no link check, nothing automated. Verification today is manual: this pass ran the 3 HTML files through Python's stdlib `html.parser` (all clean) and `python3 -m py_compile` on `automation/publish_instagram.py` (clean). Not fixed this pass — a lint/link-check workflow is real scope, better sized as its own follow-up. |
| Obs | health endpoint + smoke script + where logs live | N/A | Static site, no backend process to health-check. "Logs" are GitHub Pages' own build/deploy log (repo Settings → Pages) plus Meta Pixel events (external, Meta Events Manager) — no logs live in this repo. |
| Cost | current R$/mo + launch-day delta (LAUNCH_DAY_RUNBOOK ref) | ✅ | R$0/mo — GitHub Pages free tier, domain already owned. Hotmart's fee is per-sale (transaction cost, not hosting), already documented in `06_OPERATIONS.md` §Costs. No launch-day cost delta — this repo has no paid switches to flip. |
| Contract | .boss/app.manifest.yaml valid vs schema | N/A | No `.boss/app.manifest.yaml` in this repo — this is a public static marketing site, not a BOSS-integrated internal app. Confirmed absent (not "missing"): `find . -iname "app.manifest.yaml"` returns nothing, and nothing in this repo's docs claims one should exist. |
| Kit | CLAUDE.md/AGENTS.md truthful (commands run as written) | ✅ | Installed this pass; the only command in the kit (`python3 -m py_compile automation/publish_instagram.py`) was actually run and verified clean before being written down. |
| Stack | mission-brief description matches repo reality | ✅ | Mission brief described this repo as Next.js; verified this pass it is plain static HTML/CSS/JS (no `package.json`, no framework manifest anywhere in the tree). Corrected in `CLAUDE.md`/`AGENTS.md` so the mismatch isn't inherited by a future session. |

## Legend
✅ verified this pass · 🟡 gap noted, not blocking · ❌ real gap, not fixed this pass · N/A doesn't
apply to this app's shape (with reason given, not left blank)
