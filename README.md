# fabrica-de-agentes — site público

Landing page do **Pack Fábrica de Agentes** (IDEA-006.F1 / Engineering Guild), servida via GitHub Pages.

- Produto, conteúdo e docs: repo privado [`idea-006-fabrica-de-agentes`](https://github.com/EngineeringGuild/idea-006-fabrica-de-agentes)
- Issue do lançamento: ENG-140 · Decisões: DEC-F1-002 (checkout Hotmart/Gumroad), DEC-F1-003 (Pages até decisão de domínio)

## Estrutura

| Caminho | Página |
|---|---|
| `/` | LP da oferta (R$ 47 lançamento) |
| `/gratis/` | Lead magnet — Agentes 01, 02 e 04 (captura por Brevo, PDFs por email — ver nota HITL no HTML) |
| `/obrigado/` | Pós-compra (configurar como página de obrigado na Hotmart) |
| `/downloads/` | Arquivos públicos (lead magnet) — 3 PDFs (Agentes 01/02/04) |

## Deploy

Pages serve a branch `main` (root). Editar → commit em `main` → ~1 min no ar.

**Trocar o CTA quando o checkout Hotmart existir:** em `index.html`, anchors `#cta-hero` e `#cta-comprar` → URL do checkout; remover nota "checkout abre hoje" e mudar availability do JSON-LD para `InStock`.
