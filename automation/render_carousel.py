#!/usr/bin/env python3
"""
render_carousel.py — Renderiza os slides dos carrosséis do @fabricadeagentesai em PNG.

Motivação: o gargalo de publicação diária não é escrever o post — é PRODUZIR a imagem.
7 posts x ~7 slides = ~49 artes no Canva. Este script gera todas em segundos, com a
identidade visual da LP (mesmas cores do style.css), prontas para upload.

Além dos PNGs, emite por pasta:
    caption.txt  — a legenda pronta para colar no Planner do Business Suite
    alt.txt      — o texto alternativo de cada slide (a busca do Instagram indexa alt text)

Fonte do conteúdo (project-money, repo separado — se editar lá, editar aqui):
    docs/factories/f-video/scripts/batch-fabricadeagentes-02-carrossel.md   (lote 2, posts 1-7)
    docs/factories/f-video/scripts/batch-fabricadeagentes-03-atracao.md     (lote 3, posts 8-15)

## Lint (roda antes de renderizar, falha barato)

Três regras vieram da pesquisa de plataforma (project-money/docs/research/IG_PLATFORM_RESEARCH_2026-08.md):

  1. SLIDE 2 PRECISA DE TÍTULO PRÓPRIO. Mosseri confirmou que o Instagram re-exibe o
     carrossel começando pelo slide 2 para quem viu e não deslizou — ou seja, o slide 2
     é uma segunda capa. Continuação de frase ali é alcance jogado fora.
  2. NO MÁXIMO 5 HASHTAGS. Teto duro da plataforma desde dez/2025.
  3. LEGENDA ATÉ 2200 CARACTERES. Limite da API (ver publish_carousel.py:132).

E um aviso (não falha): se o corpo de fonte cair abaixo de MIN_FONT_WARN, o texto do
slide é longo demais para ser lido no feed — corta o texto, não aceita a fonte menor.

Sem dependência externa além de Pillow (já instalada). Fontes: Segoe UI (Windows).

Uso:
    python render_carousel.py                       # lote 3 em ./tmp/carrossel/
    python render_carousel.py --batch 2             # lote 2
    python render_carousel.py --lint                # só valida, não renderiza
    python render_carousel.py --out DIR             # diretório de saída
    python render_carousel.py --post 9              # só o post 9

Saída: <out>/post-N/slide-NN.png (1080x1350, 4:5) + caption.txt + alt.txt
"""
from __future__ import annotations

import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- identidade
W, H = 1080, 1350
INK = (16, 21, 29)          # #10151d — fundo padrão (igual --ink da LP)
WHITE = (255, 255, 255)
AMBER = (232, 176, 75)      # #e8b04b — igual --accent da LP
MARGIN = 92

# Abaixo disso o texto ainda "cabe", mas não se lê no feed. Vira aviso, não erro.
MIN_FONT_WARN = 40

FONT_DIR = r"C:\Windows\Fonts"
F_BOLD = os.path.join(FONT_DIR, "segoeuib.ttf")
F_REG = os.path.join(FONT_DIR, "segoeui.ttf")
if not os.path.exists(F_BOLD):                       # fallback
    F_BOLD, F_REG = os.path.join(FONT_DIR, "arialbd.ttf"), os.path.join(FONT_DIR, "arial.ttf")

HANDLE = "@fabricadeagentesai"
SLOT = "11:30 BRT"

MAX_HASHTAGS = 5
MAX_CAPTION = 2200
MAX_SLIDES = 10          # teto do publish_carousel.py; o IG hoje aceita 20


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Quebra texto em linhas que cabem em max_w."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_block(draw, text, path, max_w, max_h, start, min_size=30):
    """Acha o maior corpo de fonte em que o texto ainda cabe na caixa."""
    size = start
    while size >= min_size:
        fnt = font(path, size)
        lines = wrap(draw, text, fnt, max_w)
        lh = int(size * 1.22)
        if len(lines) * lh <= max_h:
            return fnt, lines, lh
        size -= 2
    fnt = font(path, min_size)
    return fnt, wrap(draw, text, fnt, max_w), int(min_size * 1.22)


def render(slide: dict, idx: int, total: int, out: str, series: str | None = None) -> int:
    """Renderiza um slide. Devolve o menor corpo de fonte usado (para o aviso de legibilidade)."""
    cta = slide.get("cta", False)
    bg, fg, accent = (AMBER, INK, INK) if cta else (INK, WHITE, AMBER)

    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)
    box_w = W - 2 * MARGIN

    # barra de destaque no topo
    d.rectangle([MARGIN, 150, MARGIN + 130, 162], fill=accent)

    # Selo da série ao lado da barra. Série tem nome próprio e cadência fixa — o selo é
    # o que faz a pessoa reconhecer o formato antes de ler (FORMAT_BANK.md).
    if series:
        fseal = font(F_BOLD, 26)
        d.text((MARGIN + 130 + 26, 143), f"{series} · {idx:02d}", font=fseal, fill=accent)

    # Área útil entre a barra de destaque e o rodapé. O bloco é medido primeiro e
    # depois centralizado verticalmente — sem isso o texto encosta no topo e sobra
    # um vazio grande embaixo (ruim no feed, onde o slide é visto inteiro).
    TOP, BOTTOM = 240, H - 190
    avail = BOTTOM - TOP
    GAP = 34

    title, body = slide.get("title"), slide.get("body")
    blocks, total_h, smallest = [], 0, 999

    if title:
        f, lines, lh = fit_block(d, title, F_BOLD, box_w, int(avail * 0.60), 84, 44)
        blocks.append((f, lines, lh))
        total_h += len(lines) * lh
        smallest = min(smallest, f.size)
    if body:
        room = avail - total_h - (GAP if title else 0)
        f, lines, lh = fit_block(d, body, F_REG if title else F_BOLD, box_w, room,
                                 62 if title else 76, 30)
        blocks.append((f, lines, lh))
        total_h += len(lines) * lh + (GAP if title else 0)
        smallest = min(smallest, f.size)

    y = TOP + max(0, (avail - total_h) // 2)
    for i, (f, lines, lh) in enumerate(blocks):
        if i:
            y += GAP
        for ln in lines:
            d.text((MARGIN, y), ln, font=f, fill=fg)
            y += lh

    # rodapé: contador + marca d'água
    fs = font(F_BOLD, 30)
    d.text((MARGIN, H - 108), f"{idx:02d}/{total:02d}", font=fs, fill=accent)
    fw = font(F_REG, 28)
    tw = d.textlength(HANDLE, font=fw)
    wm = Image.new("RGBA", (int(tw) + 8, 44), (0, 0, 0, 0))
    ImageDraw.Draw(wm).text((0, 0), HANDLE, font=fw,
                            fill=(*accent, 160) if not cta else (*INK, 150))
    img.paste(wm, (W - MARGIN - int(tw), H - 106), wm)

    img.save(out, "PNG", optimize=True)
    return smallest


# ---------------------------------------------------------------- lint


def lint(post: dict) -> list[str]:
    """Erros que impedem a publicação. Lista vazia = passou."""
    errs, pid = [], post["id"]
    slides = post["slides"]

    if not slides:
        errs.append(f"post {pid}: sem slides")
    if len(slides) > MAX_SLIDES:
        errs.append(f"post {pid}: {len(slides)} slides (máx {MAX_SLIDES})")

    # A regra da segunda capa: o IG re-exibe o carrossel a partir do slide 2.
    # O lote 2 é isento: foi escrito antes desta regra existir e JÁ ESTÁ AGENDADO no
    # Planner. Reescrever aqui faria o repo divergir do que vai ao ar — pior que o
    # alcance perdido. A regra vale do lote 3 em diante.
    if not post.get("legacy") and len(slides) >= 2 and not slides[1].get("title"):
        errs.append(
            f"post {pid}: slide 2 sem título — ele é a SEGUNDA CAPA (o Instagram re-exibe "
            f"o carrossel a partir dele). Precisa de um gancho próprio, não continuação."
        )

    cap = post.get("caption", "")
    if not cap.strip():
        errs.append(f"post {pid}: sem legenda")
    if len(cap) > MAX_CAPTION:
        errs.append(f"post {pid}: legenda com {len(cap)} chars (máx {MAX_CAPTION})")
    n_tags = cap.count("#")
    if n_tags > MAX_HASHTAGS:
        errs.append(f"post {pid}: {n_tags} hashtags (teto da plataforma é {MAX_HASHTAGS})")

    return errs


def slide_text(s: dict) -> str:
    return " ".join(p for p in (s.get("title"), s.get("body")) if p)


def write_sidecars(post: dict, d: str) -> None:
    """caption.txt (colar no Planner) e alt.txt (texto alternativo, indexado pela busca)."""
    with open(os.path.join(d, "caption.txt"), "w", encoding="utf-8") as fh:
        fh.write(post["caption"])
        fh.write(f"\n\n---\nAgendado: {post['date']} {SLOT}  |  {post['title']}\n")

    with open(os.path.join(d, "alt.txt"), "w", encoding="utf-8") as fh:
        fh.write("# Texto alternativo — colar no campo de cada slide ao agendar.\n")
        fh.write("# A busca do Instagram indexa alt text. Se o app cortar, mantenha a 1a frase.\n\n")
        for i, s in enumerate(post["slides"], 1):
            fh.write(f"slide {i:02d}: {slide_text(s)}\n")


# ---------------------------------------------------------------- conteúdo
#
# LOTE 2 — linha de CONVERSÃO (12→18/08). Agendado no Planner do Business Suite em 11/08.
# NÃO EDITAR o texto: é o que já está no ar. Mantido aqui para o caption.txt ser reprodutível.

LOTE_2 = [
    {
        "id": 1, "date": "2026-08-12", "title": "3 horas -> 4 minutos (demo)", "series": None,
        "legacy": True,
        "caption": (
            "Eu levava 3 horas nisso. Agora levo 4 minutos — e a diferença não foi trocar de ferramenta.\n\n"
            "A maioria das pessoas pede \"escreve um post pra mim\" e recebe texto genérico com emoji de "
            "foguete. O problema não é a IA. É usá-la sem manual.\n\n"
            "Agente é a mesma IA contratada direito: quem ela é, o que sabe do seu negócio, o que nunca pode "
            "fazer, e o formato que tem que devolver. Escrevi 10 desses pra minha própria operação.\n\n"
            "Comenta AGENTE que eu te mando 3 agentes prontos, de graça (sem programar nada).\n\n"
            "#agentesdeIA #automação #IAparaNegócios #produtividade"
        ),
        "slides": [
            {"title": "EU LEVAVA 3 HORAS NISSO.", "body": "Agora levo 4 minutos."},
            {"body": "Escrever 5 posts da semana era: abrir doc em branco, lembrar o tom, escrever, revisar — e travar no terceiro."},
            {"body": "Aí eu parei de pedir \u201cescreve um post pra mim\u201d."},
            {"body": "Passei a CONTRATAR a IA: quem ela é, o que sabe do meu negócio, o que nunca pode fazer, e o formato exato de saída."},
            {"body": "Isso tem nome: agente. É a mesma IA — com manual de funcionário."},
            {"body": "Dou 5 temas. Recebo 5 posts prontos no meu tom. 4 minutos."},
            {"title": "Comenta AGENTE", "body": "que eu te mando 3 agentes prontos, de graça.", "cta": True},
        ],
    },
    {
        "id": 2, "date": "2026-08-13", "title": "3 agentes que você monta hoje (listicle)", "series": None,
        "legacy": True,
        "caption": (
            "3 agentes prontos que você monta hoje, sem programar nada.\n\n"
            "Atendente, follow-up de orçamento e gerador de conteúdo. Os três rodam nas contas gratuitas que "
            "você já tem — o que muda é o manual que você cola dentro.\n\n"
            "Esses 3 são os que eu libero de graça, completos. Não é amostra cortada.\n\n"
            "Comenta AGENTE que eu te mando os 3.\n\n"
            "#agentesdeIA #automação #pequenosnegócios #IAparaNegócios"
        ),
        "slides": [
            {"title": "3 AGENTES QUE VOCÊ MONTA HOJE.", "body": "Sem programar. Sem mensalidade nova."},
            {"title": "1. ATENDENTE", "body": "Responde as perguntas repetidas do WhatsApp em segundos, no seu tom — e te chama quando é venda ou problema."},
            {"title": "2. FOLLOW-UP", "body": "A maioria das vendas não é recusada. É esquecida. Ele lembra do orçamento parado por você."},
            {"title": "3. CONTEÚDO", "body": "Calendário de 30 dias + posts prontos, a partir do que o seu negócio realmente faz."},
            {"body": "Todos rodam no plano GRATUITO do ChatGPT, Claude ou Gemini. Você já tem a ferramenta."},
            {"body": "O que falta não é IA. É o manual de cada um."},
            {"title": "Comenta AGENTE", "body": "que eu te mando os 3 prontos, de graça.", "cta": True},
        ],
    },
    {
        "id": 3, "date": "2026-08-14", "title": "Perdeu a venda pela demora (dor)", "series": None,
        "legacy": True,
        "caption": (
            "Todo pequeno negócio perde venda por demora no WhatsApp — e quase nunca percebe, porque o cliente "
            "não avisa que desistiu.\n\n"
            "O que resolve não é acordar mais cedo. É ter um atendente que responde no seu tom, sabe seu preço "
            "e seu prazo, e que escala pra você quando é venda ou problema. Sem inventar resposta — essa é a "
            "regra que faz ele ser confiável.\n\n"
            "Comenta AGENTE que eu te mando 3 agentes prontos, de graça.\n\n"
            "#atendimento #whatsappbusiness #agentesdeIA #pequenosnegócios"
        ),
        "slides": [
            {"title": "VOCÊ NÃO PERDEU A VENDA PELO PREÇO.", "body": "Perdeu pela demora."},
            {"body": "O cliente manda \u201cquanto custa?\u201d às 21h. Você responde às 9h do dia seguinte."},
            {"body": "Nesse intervalo ele mandou a mesma pergunta pra mais dois. Quem respondeu primeiro levou."},
            {"body": "Você não precisa responder mais rápido. Precisa que ALGO responda por você enquanto você vive."},
            {"body": "Um atendente que sabe seu preço, seu prazo, sua política — e que nunca inventa quando não sabe: ele te passa a bola."},
            {"body": "Leva 20 minutos pra montar. Trabalha 24h. Custa R$0/mês."},
            {"title": "Comenta AGENTE", "body": "que eu te mando 3 agentes prontos, de graça.", "cta": True},
        ],
    },
    {
        "id": 4, "date": "2026-08-15", "title": "O estagiário de R$0 e o que eu proibi", "series": None,
        "legacy": True,
        "caption": (
            "Contratei um estagiário que custa R$0/mês. A parte que ninguém mostra é o que eu proibi ele de "
            "fazer.\n\n"
            "Todo agente que eu escrevo tem as duas listas: o que ele faz e o que ele nunca pode fazer. O "
            "atendente não inventa resposta. O financeiro não dá conselho de investimento. O de prospecção "
            "respeita o \"não\" do lead e a LGPD.\n\n"
            "Delegar sem essa segunda lista é como dar a chave da loja pra alguém no primeiro dia.\n\n"
            "Comenta AGENTE que eu te mando 3 agentes prontos, de graça.\n\n"
            "#automação #agentesdeIA #IAparaNegócios #produtividade"
        ),
        "slides": [
            {"title": "CONTRATEI UM ESTAGIÁRIO DE R$0/MÊS.", "body": "Olha o que eu entreguei pra ele."},
            {"body": "Regra que eu segui: só delego o que eu já sei fazer e odeio fazer."},
            {"title": "ENTROU NA LISTA", "body": "Responder pergunta repetida. Lembrar orçamento parado. Rascunhar post. Organizar entrada e saída da semana."},
            {"title": "FICOU DE FORA", "body": "Falar preço final. Prometer prazo. Dar conselho de dinheiro. Qualquer coisa que assine meu nome sem eu ver."},
            {"body": "Essa segunda lista é a parte que quase ninguém escreve — e é ela que impede o vexame."},
            {"body": "Um agente sem \u201co que nunca fazer\u201d não é funcionário. É risco."},
            {"title": "Comenta AGENTE", "body": "que eu te mando 3 agentes prontos, de graça.", "cta": True},
        ],
    },
    {
        "id": 5, "date": "2026-08-16", "title": "Filmei sem corte (apoio do Reel)", "series": None,
        "legacy": True,
        "caption": (
            "Filmei o agente resolvendo em tempo real, sem corte e com cronômetro. Não é demo de propaganda — "
            "é a tarefa que eu faço toda semana.\n\n"
            "O que faz ele acertar o tom não é o pedido. É o manual que já está dentro dele.\n\n"
            "Comenta AGENTE que eu te mando 3 agentes prontos, de graça.\n\n"
            "#agentesdeIA #automação #IAparaNegócios"
        ),
        "slides": [
            {"title": "FILMEI SEM CORTE.", "body": "Cronômetro rodando na tela."},
            {"body": "5 temas. É só o que eu dou pra ele."},
            {"body": "Ele já sabe meu tom, meu público e o que eu nunca falo — isso está escrito no agente, não no pedido."},
            {"body": "5 posts prontos. Vou revisar, não reescrever."},
            {"title": "Comenta AGENTE", "body": "que eu te mando 3 agentes prontos, de graça.", "cta": True},
        ],
    },
    {
        "id": 6, "date": "2026-08-17", "title": "Engenheiro, 2 horas, o molde (autoridade)", "series": None,
        "legacy": True,
        "caption": (
            "Sou engenheiro mecatrônico e levei 2 horas pra montar o meu primeiro agente. Não foi escrevendo — "
            "foi descobrindo o que precisava estar escrito.\n\n"
            "Tom, contexto do negócio, limites, formato de saída e o que fazer quando não souber a resposta. "
            "Esse é o molde. Depois que ele existe, o próximo agente leva 20 minutos.\n\n"
            "Comenta AGENTE que eu te mando 3 agentes prontos, de graça — já no molde.\n\n"
            "#agentesdeIA #engenharia #automação #IAparaNegócios"
        ),
        "slides": [
            {"title": "LEVEI 2 HORAS PRA MONTAR O PRIMEIRO.", "body": "Você leva 20 minutos."},
            {"body": "Sou engenheiro mecatrônico. Passei a carreira fazendo máquina repetir processo sem errar."},
            {"body": "Agente é a mesma coisa, em texto: entrada definida, regra clara, saída previsível."},
            {"body": "As 2 horas do primeiro não foram escrevendo. Foram descobrindo O QUE precisava estar escrito."},
            {"body": "Tom. Contexto do negócio. Limites. Formato de saída. O que fazer quando não souber."},
            {"body": "Depois que o molde existe, o próximo agente sai em 20 minutos. Por isso eu escrevi 10."},
            {"title": "Comenta AGENTE", "body": "que eu te mando 3 agentes prontos, de graça.", "cta": True},
        ],
    },
    {
        "id": 7, "date": "2026-08-18", "title": "Quanto custa alguém 24/7 (conta na mesa)", "series": None,
        "legacy": True,
        "caption": (
            "Quanto custa alguém respondendo mensagem 24/7? Fiz a conta na frente de vocês — e o ponto não é "
            "\"demita alguém\".\n\n"
            "É que existe uma faixa de trabalho repetido que não deveria consumir nem o seu tempo nem o salário "
            "de ninguém. Pergunta que se repete, orçamento que precisa de lembrete, post que precisa sair toda "
            "semana.\n\n"
            "Isso um agente segura. O resto continua sendo humano.\n\n"
            "Comenta AGENTE que eu te mando 3 agentes prontos, de graça.\n\n"
            "#agentesdeIA #gestão #pequenosnegócios #automação"
        ),
        "slides": [
            {"title": "QUANTO CUSTA ALGUÉM RESPONDENDO 24/7?", "body": "Fiz a conta na sua frente."},
            {"body": "Meio período só pra responder mensagem: salário, encargos, treinamento — e o seu tempo gerenciando."},
            {"body": "E ainda assim: dorme, folga, adoece, e um dia pede demissão levando o que aprendeu."},
            {"body": "Agente: responde 24/7, não esquece o que aprendeu, e o que ele sabe fica escrito num arquivo SEU."},
            {"body": "Não é substituto de gente. É o que segura o operacional repetido enquanto você faz o que só você faz."},
            {"body": "Custo da ferramenta: R$0. O que custa é o manual — e ele já está escrito."},
            {"title": "Comenta AGENTE", "body": "que eu te mando 3 agentes prontos, de graça.", "cta": True},
        ],
    },
]

# LOTE 3 — linha de ATRAÇÃO (19→25/08). 6 de atração : 1 de conversão.
# Regras novas: slide 2 é segunda capa · nenhum post de atração pede engajamento ·
# CTA só na linha de conversão. Racional em FORMAT_BANK.md e IG_PLATFORM_RESEARCH_2026-08.md.

LOTE_3 = [
    {
        "id": 8, "date": "2026-08-19", "title": "A linha: as 3 perguntas que faltam", "series": "A LINHA",
        "caption": (
            "Como fazer o ChatGPT parar de chutar resposta: uma linha no fim do pedido.\n\n"
            "\"Antes de responder, me faça as 3 perguntas que faltam pra você acertar.\"\n\n"
            "Em vez de inventar o que faltou, ela pergunta. E as perguntas que ela faz costumam ser exatamente "
            "as que você esqueceu de responder.\n\n"
            "O problema quase nunca é a ferramenta. É que ela recebeu metade do contexto e não tinha permissão "
            "de pedir o resto.\n\n"
            "Esse aqui é pra quem já reescreveu o mesmo pedido quatro vezes achando que estava explicando mal.\n\n"
            "#chatgpt #IAparaNegócios #produtividade #automação"
        ),
        "slides": [
            {"title": "A IA TE RESPONDE BONITO E INÚTIL?", "body": "Falta uma linha."},
            {"title": "\u201cAntes de responder, me faça as 3 perguntas que faltam pra você acertar.\u201d"},
            {"body": "Cola isso no fim de qualquer coisa que você pedir."},
            {"body": "Ela para de chutar e começa a perguntar. É o que um funcionário bom faz no primeiro dia."},
            {"body": "Funciona porque o problema quase nunca é a ferramenta. É que ela recebeu metade do contexto e não tinha permissão de pedir o resto."},
        ],
    },
    {
        "id": 9, "date": "2026-08-20", "title": "POV: oi às 22h47", "series": "POV",
        "caption": (
            "Perder venda no WhatsApp por demora: todo mundo que atende cliente já viveu o \"oi\" das 22h47.\n\n"
            "Você acorda, responde educado, capricha no orçamento. E a pessoa some. Não é que ela achou caro — "
            "é que às 23h05 alguém já tinha respondido.\n\n"
            "Não é falta de esforço. É que existe uma janela em que você está dormindo e o negócio continua "
            "aberto.\n\n"
            "Esse é pra quem já acordou com três \"oi\" na tela.\n\n"
            "#whatsappbusiness #pequenosnegócios #atendimento #vendas"
        ),
        "slides": [
            {"title": "POV: O CLIENTE MANDOU \u201cOI\u201d ÀS 22H47.", "body": "Você já sabe que era orçamento."},
            {"title": "VOCÊ RESPONDEU 9H12.", "body": "Ele fechou com outro às 23h05."},
            {"body": "Ninguém perde venda por preço às 23h. Perde porque estava dormindo — que é o que gente faz."},
        ],
    },
    {
        "id": 10, "date": "2026-08-21", "title": "Me corrige: o prompt ruim de propósito", "series": "ME CORRIGE",
        "caption": (
            "Prompt ruim de ChatGPT: esse aqui está errado e eu escrevi de propósito.\n\n"
            "\"Escreve uma resposta pro cliente que perguntou o preço.\"\n\n"
            "Voltou um texto simpático, sem preço, sem prazo e sem tom nenhum. E a culpa não é da ferramenta.\n\n"
            "Faltou dizer qual preço, qual cliente, que tom usar e o que fazer se ele pedir desconto. Quatro "
            "coisas que eu sei de cabeça e simplesmente não escrevi.\n\n"
            "O que mais faltou aí?\n\n"
            "#chatgpt #prompt #IAparaNegócios #pequenosnegócios"
        ),
        "slides": [
            {"title": "ESSE PROMPT ESTÁ ERRADO.", "body": "Você consegue ver onde?"},
            {"title": "\u201cEscreve uma resposta pro cliente que perguntou o preço.\u201d", "body": "É isso. Foi só isso que eu mandei."},
            {"body": "O que voltou: um texto simpático, com \u201colá!\u201d, \u201cficamos felizes com seu interesse\u201d — e nenhum preço."},
            {"body": "Faltou: qual preço. Qual cliente. Que tom. E o que fazer se ele pedir desconto."},
            {"body": "Quatro coisas que eu sei de cabeça e não escrevi. Ela não adivinha o que está na sua cabeça."},
            {"body": "Escrevi esse ruim de propósito. Mas já mandei um igual, sem querer, umas trinta vezes."},
        ],
    },
    {
        "id": 11, "date": "2026-08-22", "title": "As 5 partes de um agente (CONVERSÃO)", "series": None,
        "caption": (
            "Como montar um agente de IA pro seu negócio: são sempre as mesmas 5 partes.\n\n"
            "Quem ele é. O que sabe do seu negócio. O que ele nunca pode fazer. O formato exato da resposta. "
            "E o que fazer quando não souber.\n\n"
            "A terceira é a que quase ninguém escreve — e é ela que impede o agente de inventar preço, prometer "
            "prazo ou dar conselho que você não daria.\n\n"
            "Comenta AGENTE que eu te mando 3 agentes prontos, completos, de graça.\n\n"
            "#agentesdeIA #automação #IAparaNegócios #pequenosnegócios"
        ),
        "slides": [
            {"title": "PASSEI A SEMANA MOSTRANDO PEDAÇO.", "body": "Hoje eu mostro de onde eles saem."},
            {"title": "TODO AGENTE QUE EU ESCREVO TEM 5 PARTES.", "body": "É sempre a mesma estrutura."},
            {"body": "Quem ele é. O que sabe do seu negócio. O que nunca pode fazer. O formato exato da resposta. E o que fazer quando não souber."},
            {"body": "A terceira é a que quase ninguém escreve. A quinta é a que evita vexame."},
            {"body": "Três desses eu libero completos, de graça. Não é amostra cortada — é o arquivo inteiro."},
            {"title": "Comenta AGENTE", "body": "que eu te mando os 3 prontos.", "cta": True},
        ],
    },
    {
        "id": 12, "date": "2026-08-23", "title": "O cardápio: 8 tarefas no plano gratuito", "series": "O CARDÁPIO",
        "caption": (
            "O que a IA gratuita já faz no seu pequeno negócio: 8 tarefas, nenhuma com plano pago.\n\n"
            "Responder pergunta repetida, lembrar de orçamento parado, transformar áudio longo em lista, "
            "escrever a descrição do serviço, revisar o que você vai mandar antes de mandar.\n\n"
            "Nenhuma delas é impressionante. Todas elas são o que consome a sua terça-feira.\n\n"
            "A oitava é a que eu mais uso e a que ninguém fala: colar o texto e perguntar o que ali pode ser "
            "mal interpretado.\n\n"
            "#IAparaNegócios #chatgpt #produtividade #pequenosnegócios #automação"
        ),
        "slides": [
            {"title": "O CARDÁPIO", "body": "8 coisas que a IA já faz no seu negócio hoje. Sem plano pago."},
            {"title": "1. RESPONDER A PERGUNTA REPETIDA", "body": "As 10 que mais caem no seu WhatsApp — no seu tom, não no dela."},
            {"title": "2. LEMBRAR DO ORÇAMENTO PARADO", "body": "Você cola a lista. Ela escreve a cobrança educada de cada um."},
            {"title": "3. TRADUZIR GROSSERIA EM EDUCAÇÃO", "body": "Você escreve o que sentiu. Ela devolve o que dá pra mandar."},
            {"title": "4. VIRAR ÁUDIO EM TEXTO", "body": "O áudio de 4 minutos do cliente vira 3 linhas e uma lista do que ele pediu."},
            {"title": "5. FECHAR A SEMANA", "body": "Você joga as anotações soltas. Ela devolve o que entrou, o que saiu e o que ficou pendente."},
            {"title": "6. ESCREVER A DESCRIÇÃO DO SERVIÇO", "body": "A mesma que você nunca senta pra escrever e por isso ainda não está no site."},
            {"title": "7. FAZER A PERGUNTA QUE VOCÊ ESQUECEU", "body": "Antes do orçamento: o que falta perguntar pro cliente pra não voltar atrás depois."},
            {"title": "8. REVISAR ANTES DE VOCÊ MANDAR", "body": "Cola o texto e pergunta: \u201co que aqui pode ser mal interpretado?\u201d"},
            {"body": "Nenhuma precisa de plano pago. Todas precisam que você diga o que quer com uma frase a mais."},
        ],
    },
    {
        "id": 13, "date": "2026-08-24", "title": "Isso é normal: o arquivado do WhatsApp", "series": "ISSO É NORMAL?",
        "caption": (
            "Isso é normal? Tenho 4 orçamentos parados no arquivado do WhatsApp. Um deles é de maio.\n\n"
            "A pessoa nunca respondeu. Eu também nunca cobrei. E não é desorganização — é que \"lembrar de "
            "cobrar o orçamento parado\" não está no cargo de ninguém, então não acontece.\n\n"
            "A venda que some não avisa que sumiu. Ela só não volta.\n\n"
            "Me diz que não sou só eu.\n\n"
            "#pequenosnegócios #orçamento #whatsappbusiness #vendas"
        ),
        "slides": [
            {"title": "ISSO É NORMAL?", "body": "Tenho 4 orçamentos parados no arquivado do WhatsApp."},
            {"title": "ABRI O ARQUIVADO HOJE. ACHEI UM DE MAIO.", "body": "A pessoa nunca respondeu. Eu também nunca cobrei."},
            {"body": "Não é desorganização. É que \u201clembrar de cobrar\u201d não é tarefa de ninguém — então não é de ninguém."},
            {"body": "Me diz que não sou só eu."},
        ],
    },
    # post 14 (dom 25/08, "Semana em números") NÃO entra aqui de propósito: os números
    # são medidos no Insights no domingo. Post com número estimado não existe.
    {
        "id": 15, "date": "2026-08-26", "title": "O aviso: o que não colar na IA (RESERVA)", "series": "O AVISO",
        "caption": (
            "O que não colar no ChatGPT: dado de cliente com nome, contrato de terceiro e senha.\n\n"
            "Não é paranoia — é que o dado sai do seu controle no segundo em que você aperta enviar, e a "
            "responsabilidade sobre ele continua sendo sua.\n\n"
            "O jeito certo é trocar o dado real por marcador: [NOME], [VALOR], [PRAZO]. A resposta sai "
            "exatamente igual e o dado não sai de casa.\n\n"
            "Esse é pra quem já colou um orçamento inteiro, com nome do cliente, pra \"só melhorar a redação\".\n\n"
            "#lgpd #chatgpt #pequenosnegócios #IAparaNegócios"
        ),
        "slides": [
            {"title": "NÃO COLA ISSO NO CHATGPT.", "body": "3 coisas que eu não jogo lá dentro."},
            {"title": "1. DADO DE CLIENTE COM NOME", "body": "CPF, endereço, telefone, número de contrato. Se vazar, o problema é seu — não da ferramenta."},
            {"title": "2. CONTRATO INTEIRO DE TERCEIRO", "body": "Você pode não ter o direito de colar aquilo em lugar nenhum. Confidencialidade não some porque é IA."},
            {"title": "3. SENHA. QUALQUER UMA.", "body": "Parece óbvio. Eu já vi."},
            {"body": "O jeito certo é trocar o dado real por marcador: [NOME], [VALOR], [PRAZO]. A resposta sai igual e o dado não sai de casa."},
            {"body": "E confere na ferramenta que você usa: em várias, no plano gratuito, a conversa pode ser usada pra treinar o modelo. Costuma dar pra desligar nas configurações."},
        ],
    },
]

BATCHES = {2: LOTE_2, 3: LOTE_3}


def main() -> int:
    ap = argparse.ArgumentParser(description="Renderiza os carrosséis do @fabricadeagentesai.")
    ap.add_argument("--batch", type=int, default=3, choices=sorted(BATCHES),
                    help="qual lote renderizar (default: 3)")
    ap.add_argument("--out", default=os.path.join("tmp", "carrossel"))
    ap.add_argument("--post", type=int, help="renderizar só este post (pelo id)")
    ap.add_argument("--lint", action="store_true", help="só validar, não renderizar")
    a = ap.parse_args()

    posts = BATCHES[a.batch]
    if a.post:
        posts = [p for p in posts if p["id"] == a.post]
        if not posts:
            ids = ", ".join(str(p["id"]) for p in BATCHES[a.batch])
            print(f"post {a.post} não existe no lote {a.batch} (ids: {ids})", file=sys.stderr)
            return 1

    errs = [e for p in posts for e in lint(p)]
    if errs:
        print(f"LINT FALHOU ({len(errs)}):", file=sys.stderr)
        for e in errs:
            print(f"  ✗ {e}", file=sys.stderr)
        return 1
    print(f"lint ok: {len(posts)} posts do lote {a.batch}", file=sys.stderr)
    if a.lint:
        return 0

    total_files, warns = 0, []
    for p in posts:
        slides = p["slides"]
        d = os.path.join(a.out, f"post-{p['id']}")
        os.makedirs(d, exist_ok=True)
        for i, s in enumerate(slides, 1):
            path = os.path.join(d, f"slide-{i:02d}.png")
            size = render(s, i, len(slides), path, p.get("series"))
            if size < MIN_FONT_WARN:
                warns.append(f"post {p['id']} slide {i}: fonte {size}px — texto longo demais pro feed")
            total_files += 1
        write_sidecars(p, d)
        print(f"post {p['id']}: {len(slides)} slides + caption.txt + alt.txt -> {d}")

    if warns:
        print(f"\nAVISOS DE LEGIBILIDADE ({len(warns)}) — corte o texto, não aceite a fonte menor:",
              file=sys.stderr)
        for w in warns:
            print(f"  ! {w}", file=sys.stderr)

    print(f"\n{total_files} imagens geradas (1080x1350).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
