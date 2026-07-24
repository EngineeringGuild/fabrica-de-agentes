# CLAUDE.md — fabrica-de-agentes · quartel kit

> Battalion: **fabrica-de-agentes** (IDEA-006.F1, part of the Project Money cash lane). The public
> conversion surface for the Pack Fábrica de Agentes offer — landing page, lead magnet, thank-you
> page, tracking pixel. Served by GitHub Pages.

## What this repo is

- **Plain static HTML/CSS/JS. No framework, no build step, no `node_modules`.** (An earlier mission
  brief for this ARCH-PASS described this repo as Next.js — verified this pass to be inaccurate; do
  not assume a framework or package manager is present.)
- **`index.html`** — the offer LP (R$47 launch price), CTAs (`#cta-hero`, `#cta-comprar`) already
  point at the live Hotmart checkout (`pay.hotmart.com/C106375857V`).
- **`/gratis/`** — lead magnet (3 of the 10 agent PDFs), captures via an embedded Brevo form
  (`#brevo-form`, posts to a `sibforms.com` endpoint — the automation itself lives in Brevo, not this
  repo).
- **`/obrigado/`** — post-purchase page, configured as the Hotmart thank-you redirect.
- **`pixel.js`** — Meta Pixel loader, self-gating on `window.FB_PIXEL_ID` (already filled in, a public
  ID, not a secret).
- **`automation/publish_instagram.py`** — a standalone script, not wired into the site build or any
  CI (there is no CI in this repo).
- **Product content, full decision log (`DEC-F1-*`), and internal strategy live elsewhere**: the
  private repo `idea-006-fabrica-de-agentes` and `project-money` (the IDEA-006 umbrella). This repo
  covers only the LP itself, its deploy, and its SEO.

## Reading order (cold start)

1. this file → 2. `docs/00_INDEX.md` → 3. `docs/02_ARCHITECTURE.md` (includes the 2026-07-24
   ARCH-PASS addendum) → 4. the file your task names. If the task touches launch mechanics (Hotmart,
   pixel, affiliates, KPIs), read `project-money/docs/WAR_ROOM.md` first — this repo doesn't own that
   state.

## Commands (verified 2026-07-24)

```bash
python3 -m py_compile automation/publish_instagram.py   # syntax-check the one Python script in this repo
```

There is no build, lint, or test command — this is a zero-tooling static site. The closest thing to a
"test" is: open the changed `.html` file in a browser, or (as done this pass) run it through Python's
stdlib `html.parser` to catch gross markup errors. There is no CI (`.github/workflows/` doesn't
exist) — a real gap, tracked in `docs/INFRA_CHECKLIST.md`, not fixed by this kit.

## Rules

- Default branch = `main` — never commit directly; ENG-94 (branch → PR → review → merge) — though
  this repo has no CI, so "green" means the manual verify above plus a human look at the rendered
  page for any LP change (the LP is the offer's face; see the still-open PR #5 for why that PR was
  deliberately left unmerged rather than self-merged).
- **This repo is HITL-sensitive by adjacency**: it's the public face of a live launch funnel. Do not
  touch marketing copy, pricing, or checkout mechanics without a specific mandate — see
  `project-money/docs/WAR_ROOM.md` for what's currently in flight and awaiting Caio.
- Secrets: none belong in this repo. `FB_PIXEL_ID` in `pixel.js` is a public tracking ID, not a
  secret — do not treat it as one, and do not add anything that *is* a secret here.
- Add, don't delete. `docs/03_DECISIONS.md` (the `DEC-F1-*` cross-reference table) is append-only.

## Gates (what green means here)

`python3 -m py_compile automation/publish_instagram.py` clean · every changed `.html` file parses
without error (`python3 -c "import html.parser; html.parser.HTMLParser().feed(open(f).read())"` or
just open it in a browser) · any LP (`index.html`) change gets human review before merge, not just an
agent's self-check.
