---
idea: IDEA-006
doc: 03_DECISIONS
version: 0.1.0
standard: GUILD-DOC-STANDARD@0.2.0
status: active
updated: 2026-07-18
---

# fabrica-de-agentes (public site) — Decisions (DEC-F1-NNN)

Append-only. The full `DEC-F1-*` log is canonical in the private repo
`idea-006-fabrica-de-agentes`; this table cross-references only the decisions that visibly touched
**this** (public site) repo, for traceability without duplicating content this repo can't verify.

| Ref | Decision | Effect on this repo |
|---|---|---|
| DEC-F1-002 | Checkout via Hotmart/Gumroad | This site's CTA anchors link to the chosen checkout provider (Hotmart) once live — see `README.md` "Trocar o CTA" note |
| DEC-F1-003 | Stay on GitHub Pages until a domain decision | Explains why this is a plain static-site repo rather than a framework app; superseded once the custom domain (`fabricadeagentes.caiocastilho.com`) went live via `CNAME` |
| DEC-F1-006 | Build the lead magnet's other 2 agents for real (01→3) instead of adjusting the copy | `/gratis/` now serves 3 PDFs (`downloads/Agente-{01,02,04}-*-GRATIS.pdf`), not 1 — merged via `idea-006-fabrica-de-agentes#6` + this repo's `#7` |
