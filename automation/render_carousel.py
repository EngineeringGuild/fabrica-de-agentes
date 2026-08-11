#!/usr/bin/env python3
"""
render_carousel.py — Renderiza os slides dos carrosséis do @fabricadeagentesai em PNG.

Motivação: o gargalo de publicação diária não é escrever o post — é PRODUZIR a imagem.
7 posts x ~7 slides = ~49 artes no Canva. Este script gera todas em segundos, com a
identidade visual da LP (mesmas cores do style.css), prontas para upload.

Fonte do conteúdo: project-money/docs/factories/f-video/scripts/batch-fabricadeagentes-02-carrossel.md
O texto abaixo é cópia literal daquele doc — se editar o doc, editar aqui também.

Sem dependência externa além de Pillow (já instalada). Fontes: Segoe UI (Windows).

Uso:
    python render_carousel.py                      # gera tudo em ./tmp/carrossel/
    python render_carousel.py --out DIR            # diretório de saída
    python render_carousel.py --post 3             # só o post 3

Saída: tmp/carrossel/post-N/slide-NN.png  (1080x1350, 4:5)
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
BODY_TOP = 300

FONT_DIR = r"C:\Windows\Fonts"
F_BOLD = os.path.join(FONT_DIR, "segoeuib.ttf")
F_REG = os.path.join(FONT_DIR, "segoeui.ttf")
if not os.path.exists(F_BOLD):                       # fallback
    F_BOLD, F_REG = os.path.join(FONT_DIR, "arialbd.ttf"), os.path.join(FONT_DIR, "arial.ttf")

HANDLE = "@fabricadeagentesai"


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


def render(slide: dict, idx: int, total: int, out: str) -> None:
    cta = slide.get("cta", False)
    bg, fg, accent = (AMBER, INK, INK) if cta else (INK, WHITE, AMBER)

    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)
    box_w = W - 2 * MARGIN

    # barra de destaque no topo
    d.rectangle([MARGIN, 150, MARGIN + 130, 162], fill=accent)

    # Área útil entre a barra de destaque e o rodapé. O bloco é medido primeiro e
    # depois centralizado verticalmente — sem isso o texto encosta no topo e sobra
    # um vazio grande embaixo (ruim no feed, onde o slide é visto inteiro).
    TOP, BOTTOM = 240, H - 190
    avail = BOTTOM - TOP
    GAP = 34

    title, body = slide.get("title"), slide.get("body")
    blocks, total_h = [], 0

    if title:
        f, lines, lh = fit_block(d, title, F_BOLD, box_w, int(avail * 0.60), 84, 44)
        blocks.append((f, lines, lh))
        total_h += len(lines) * lh
    if body:
        room = avail - total_h - (GAP if title else 0)
        f, lines, lh = fit_block(d, body, F_REG if title else F_BOLD, box_w, room,
                                 62 if title else 76, 30)
        blocks.append((f, lines, lh))
        total_h += len(lines) * lh + (GAP if title else 0)

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


# ---------------------------------------------------------------- conteúdo
POSTS = [
    # 1
    [
        {"title": "EU LEVAVA 3 HORAS NISSO.", "body": "Agora levo 4 minutos."},
        {"body": "Escrever 5 posts da semana era: abrir doc em branco, lembrar o tom, escrever, revisar — e travar no terceiro."},
        {"body": "Aí eu parei de pedir \u201cescreve um post pra mim\u201d."},
        {"body": "Passei a CONTRATAR a IA: quem ela é, o que sabe do meu negócio, o que nunca pode fazer, e o formato exato de saída."},
        {"body": "Isso tem nome: agente. É a mesma IA — com manual de funcionário."},
        {"body": "Dou 5 temas. Recebo 5 posts prontos no meu tom. 4 minutos."},
        {"title": "Comenta AGENTE", "body": "que eu te mando 3 agentes prontos, de graça.", "cta": True},
    ],
    # 2
    [
        {"title": "3 AGENTES QUE VOCÊ MONTA HOJE.", "body": "Sem programar. Sem mensalidade nova."},
        {"title": "1. ATENDENTE", "body": "Responde as perguntas repetidas do WhatsApp em segundos, no seu tom — e te chama quando é venda ou problema."},
        {"title": "2. FOLLOW-UP", "body": "A maioria das vendas não é recusada. É esquecida. Ele lembra do orçamento parado por você."},
        {"title": "3. CONTEÚDO", "body": "Calendário de 30 dias + posts prontos, a partir do que o seu negócio realmente faz."},
        {"body": "Todos rodam no plano GRATUITO do ChatGPT, Claude ou Gemini. Você já tem a ferramenta."},
        {"body": "O que falta não é IA. É o manual de cada um."},
        {"title": "Comenta AGENTE", "body": "que eu te mando os 3 prontos, de graça.", "cta": True},
    ],
    # 3
    [
        {"title": "VOCÊ NÃO PERDEU A VENDA PELO PREÇO.", "body": "Perdeu pela demora."},
        {"body": "O cliente manda \u201cquanto custa?\u201d às 21h. Você responde às 9h do dia seguinte."},
        {"body": "Nesse intervalo ele mandou a mesma pergunta pra mais dois. Quem respondeu primeiro levou."},
        {"body": "Você não precisa responder mais rápido. Precisa que ALGO responda por você enquanto você vive."},
        {"body": "Um atendente que sabe seu preço, seu prazo, sua política — e que nunca inventa quando não sabe: ele te passa a bola."},
        {"body": "Leva 20 minutos pra montar. Trabalha 24h. Custa R$0/mês."},
        {"title": "Comenta AGENTE", "body": "que eu te mando 3 agentes prontos, de graça.", "cta": True},
    ],
    # 4
    [
        {"title": "CONTRATEI UM ESTAGIÁRIO DE R$0/MÊS.", "body": "Olha o que eu entreguei pra ele."},
        {"body": "Regra que eu segui: só delego o que eu já sei fazer e odeio fazer."},
        {"title": "ENTROU NA LISTA", "body": "Responder pergunta repetida. Lembrar orçamento parado. Rascunhar post. Organizar entrada e saída da semana."},
        {"title": "FICOU DE FORA", "body": "Falar preço final. Prometer prazo. Dar conselho de dinheiro. Qualquer coisa que assine meu nome sem eu ver."},
        {"body": "Essa segunda lista é a parte que quase ninguém escreve — e é ela que impede o vexame."},
        {"body": "Um agente sem \u201co que nunca fazer\u201d não é funcionário. É risco."},
        {"title": "Comenta AGENTE", "body": "que eu te mando 3 agentes prontos, de graça.", "cta": True},
    ],
    # 5 — dia do Reel; carrossel de apoio caso o vídeo não saia
    [
        {"title": "FILMEI SEM CORTE.", "body": "Cronômetro rodando na tela."},
        {"body": "5 temas. É só o que eu dou pra ele."},
        {"body": "Ele já sabe meu tom, meu público e o que eu nunca falo — isso está escrito no agente, não no pedido."},
        {"body": "5 posts prontos. Vou revisar, não reescrever."},
        {"title": "Comenta AGENTE", "body": "que eu te mando 3 agentes prontos, de graça.", "cta": True},
    ],
    # 6
    [
        {"title": "LEVEI 2 HORAS PRA MONTAR O PRIMEIRO.", "body": "Você leva 20 minutos."},
        {"body": "Sou engenheiro mecatrônico. Passei a carreira fazendo máquina repetir processo sem errar."},
        {"body": "Agente é a mesma coisa, em texto: entrada definida, regra clara, saída previsível."},
        {"body": "As 2 horas do primeiro não foram escrevendo. Foram descobrindo O QUE precisava estar escrito."},
        {"body": "Tom. Contexto do negócio. Limites. Formato de saída. O que fazer quando não souber."},
        {"body": "Depois que o molde existe, o próximo agente sai em 20 minutos. Por isso eu escrevi 10."},
        {"title": "Comenta AGENTE", "body": "que eu te mando 3 agentes prontos, de graça.", "cta": True},
    ],
    # 7
    [
        {"title": "QUANTO CUSTA ALGUÉM RESPONDENDO 24/7?", "body": "Fiz a conta na sua frente."},
        {"body": "Meio período só pra responder mensagem: salário, encargos, treinamento — e o seu tempo gerenciando."},
        {"body": "E ainda assim: dorme, folga, adoece, e um dia pede demissão levando o que aprendeu."},
        {"body": "Agente: responde 24/7, não esquece o que aprendeu, e o que ele sabe fica escrito num arquivo SEU."},
        {"body": "Não é substituto de gente. É o que segura o operacional repetido enquanto você faz o que só você faz."},
        {"body": "Custo da ferramenta: R$0. O que custa é o manual — e ele já está escrito."},
        {"title": "Comenta AGENTE", "body": "que eu te mando 3 agentes prontos, de graça.", "cta": True},
    ],
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join("tmp", "carrossel"))
    ap.add_argument("--post", type=int, help="renderizar só este post (1-7)")
    a = ap.parse_args()

    targets = [a.post] if a.post else range(1, len(POSTS) + 1)
    total_files = 0
    for n in targets:
        if not 1 <= n <= len(POSTS):
            print(f"post {n} não existe (1-{len(POSTS)})", file=sys.stderr)
            return 1
        slides = POSTS[n - 1]
        d = os.path.join(a.out, f"post-{n}")
        os.makedirs(d, exist_ok=True)
        for i, s in enumerate(slides, 1):
            p = os.path.join(d, f"slide-{i:02d}.png")
            render(s, i, len(slides), p)
            total_files += 1
        print(f"post {n}: {len(slides)} slides -> {d}")
    print(f"\n{total_files} imagens geradas (1080x1350).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
