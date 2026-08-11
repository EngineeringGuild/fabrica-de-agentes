---
idea: IDEA-006
doc: 01_VISION
version: 0.1.0
standard: GUILD-DOC-STANDARD@0.2.0
status: active
updated: 2026-07-18
---

# fabrica-de-agentes (public site) — Vision

## What it is

The public landing page for the **Pack Fábrica de Agentes** offer: 10 AI agent prompts (business
automation — FAQ, social content, follow-up, etc.), sold as a low-ticket info-product (R$47 launch
price) with a free lead magnet (3 of the 10 agents) as the top of funnel.

## Who it's for

Small business owners / solo operators in Brazil looking to automate customer-facing and content
workflows with AI without building anything themselves — the entry rung of IDEA-006's mini-factory
ladder (see `project-money/docs/01_VISION.md` for the umbrella-level vision).

## Non-goals (for this repo specifically)

- Not the product content itself (prompts, PDFs beyond what's needed for the free lead magnet) — that
  lives in the private repo.
- Not the marketing strategy/funnel design — that lives in `project-money/docs/marketing/` and
  `project-money/docs/WAR_ROOM.md`.
- Not an app — pure static site, no backend beyond third-party integrations (Brevo capture, Hotmart
  checkout, Meta Pixel).

## Success criteria

Visitors → `/gratis/` lead capture → Brevo email sequence → `/` checkout → Hotmart purchase →
`/obrigado/`. First real sale is the current blocker (see `04_ROADMAP.md`), not this site's build.
