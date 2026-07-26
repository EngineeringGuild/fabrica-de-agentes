# AGENTS.md — fabrica-de-agentes (for non-Claude agents)

Same content contract as `CLAUDE.md`, minimum form:

- **WHAT:** public GitHub Pages static site for the Pack Fábrica de Agentes offer (IDEA-006.F1) —
  landing page, lead magnet (`/gratis/`), thank-you page (`/obrigado/`), Meta Pixel. **Plain static
  HTML/CSS/JS, no framework, no build step** — do not assume Next.js or any package manager is
  present.
- **WHERE TO START:** `CLAUDE.md` → `docs/00_INDEX.md` → `docs/02_ARCHITECTURE.md`. Product content
  and the full `DEC-F1-*` decision log live in the private `idea-006-fabrica-de-agentes` repo and in
  `project-money`, not here.
- **COMMANDS:** `python3 -m py_compile automation/publish_instagram.py` (the only script in this
  repo). No build/lint/test command exists — verify HTML changes by opening the file in a browser.
- **NEVER:** commit to `main` without review · self-merge an LP (`index.html`) content change (the
  LP is the offer's face — human review required, see PR #5) · touch pricing/checkout/pixel
  mechanics without a specific mandate (this repo is adjacent to a live launch funnel — see
  `project-money/docs/WAR_ROOM.md`) · add secrets to this repo (there are none today; `FB_PIXEL_ID`
  is a public tracking ID, not a secret) · spend/schema/delete/social (RED → escalate to Caio).
- **REPORT:** `squad_report` in your `MSN-*.yaml` (in `memory-AI`) with PR link + gate output (POP
  OPS.10.003).
