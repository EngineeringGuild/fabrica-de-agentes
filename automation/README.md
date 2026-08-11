# automation/ — publicação no Instagram

Três peças:

| Arquivo | O que faz |
|---|---|
| `render_carousel.py` | gera os slides em PNG (1080×1350, identidade da LP) |
| `publish_instagram.py` | publica **imagem única** via API oficial |
| `publish_carousel.py` | publica **carrossel** (2-10 slides) + agenda + gate de aprovação |
| `schedule.json` | a agenda: data, caption, e o campo `approved` |
| `../.github/workflows/publish-carousel.yml` | dispara manual (celular) ou por cron diário |

## Onde fica a aprovação humana

A diretiva do Ptn-GRW-1 diz que publicação em social é sempre do Caio. **Esta
automação não remove isso — move para cima.** O gate é o campo `approved` do
`schedule.json`, que só vira `true` por PR mergeada por ele.

Nada com `approved: false` publica. Nem por cron, nem por disparo manual, nem se
alguém rodar o script na mão. O que a automação remove é a necessidade de ele
**estar na frente do PC na hora certa** — não a decisão de publicar.

## Ativação (Caio, uma vez só)

Sem isso o workflow roda e falha no `whoami`.

### 1. Conta

A conta precisa ser **Creator** ou Business (a API `graph.instagram.com` com
Instagram Login publica sem exigir Página do Facebook, mas não funciona em conta
pessoal). No app: Configurações → Tipo de conta → mudar para Creator.

### 2. Token

Gerar um **token long-lived** com escopo `instagram_business_content_publish`
no painel do Meta (developers.facebook.com → seu app → Instagram → API setup with
Instagram login → gerar token).

Anotar também o **IG user id** numérico que aparece junto.

> O token expira em ~60 dias. `publish_instagram.py --refresh-token` renova.
> Vale colocar um lembrete — token vencido derruba a automação em silêncio.

### 3. Secrets do repositório

Em `Settings → Secrets and variables → Actions`, criar:

| Secret | Valor |
|---|---|
| `IG_USER_ID` | o id numérico |
| `IG_ACCESS_TOKEN` | o token long-lived |

⚠️ **Nunca** commitar esses valores. Não existe nenhum secret neste repo hoje e
não deve passar a existir (regra do `CLAUDE.md`).

### 4. Actions habilitado

Este repo nunca teve workflow. Se a org bloquear Actions, o botão não aparece —
há um item pendente sobre isso no QUEUE ("liberar Actions Access na org").

## Uso

**Do celular (o caminho principal quando estiver na rua):**
app do GitHub → repo → aba Actions → "Publicar carrossel no Instagram" → *Run
workflow* → escolher o post (ou deixar vazio para o de hoje).

**Do PC:**

```bash
python automation/publish_carousel.py --list              # ver a agenda
python automation/publish_carousel.py --post 1 --dry-run  # validar sem publicar
python automation/publish_carousel.py --post 1            # publicar
python automation/publish_carousel.py --due               # publicar o de hoje
```

**Regenerar os slides** (depois de editar o texto no `render_carousel.py`):

```bash
python automation/render_carousel.py --out media/carrossel
```

## Por que as artes ficam em `media/carrossel/` e são commitadas

A Graph API não aceita upload de binário: ela exige `image_url` **publicamente
acessível**, que ela mesma baixa. Como o repo já é servido por GitHub Pages, ele é
o host de mídia mais barato que existe aqui (R$0). São artes de marketing — feitas
para ser públicas.

`tmp/carrossel/` continua no `.gitignore`: é a saída de rascunho do renderizador.

## Proteções embutidas no `publish_carousel.py`

- recusa se `approved: false`
- recusa se já existe `published_at` (impede post duplicado no cron seguinte)
- recusa caption vazia ou acima de 2200 caracteres
- recusa mais de 10 slides (limite do carrossel)
- recusa se a pasta de mídia não existe
- todas as checagens rodam **antes** da primeira chamada de API
