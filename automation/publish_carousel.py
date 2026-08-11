#!/usr/bin/env python3
"""
publish_carousel.py — Publica um CARROSSEL no Instagram via API oficial.

`publish_instagram.py` só publica imagem única. Carrossel exige outro fluxo:

    1) para cada slide: POST /{ig_user_id}/media  com is_carousel_item=true  -> container filho
    2) POST /{ig_user_id}/media  com media_type=CAROUSEL & children=id1,id2  -> container pai
    3) (poll) esperar o pai ficar FINISHED
    4) POST /{ig_user_id}/media_publish  com creation_id = container pai

Reusa `_request`, `whoami`, `wait_until_finished`, `publish` e `permalink` do
`publish_instagram.py` — nada de HTTP duplicado.

## Onde fica a aprovação humana

A diretiva do Ptn-GRW-1 diz que publicação em social é sempre do Caio. Esta
automação NÃO remove essa aprovação — ela a move para cima:

    o gate é o campo `approved: true` no automation/schedule.json,
    que só entra na main por PR mergeada pelo Caio.

Nada com `approved: false` publica, nem por cron, nem por disparo manual. O que a
automação remove é a necessidade de ele estar NA FRENTE DO PC na hora certa —
não a decisão de publicar.

Variáveis de ambiente:
    IG_USER_ID        ID numérico da conta Instagram (Creator)
    IG_ACCESS_TOKEN   token long-lived com escopo instagram_content_publish

Uso:
    python publish_carousel.py --post 1 --dry-run     # valida sem publicar
    python publish_carousel.py --post 1               # publica o post 1
    python publish_carousel.py --due                  # publica o agendado para hoje
    python publish_carousel.py --list                 # mostra a agenda e o estado
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
from datetime import date, datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from publish_instagram import (  # noqa: E402
    BASE,
    IGError,
    _request,
    permalink,
    publish,
    wait_until_finished,
    whoami,
)

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SCHEDULE = os.path.join(HERE, "schedule.json")


def load_schedule() -> dict:
    with open(SCHEDULE, encoding="utf-8") as fh:
        return json.load(fh)


def slide_urls(cfg: dict, post: dict) -> list[str]:
    """URLs públicas dos slides. A Graph API exige image_url acessível por ela."""
    base = cfg["media_base_url"].rstrip("/")
    d = os.path.join(REPO, post["media_dir"])
    if not os.path.isdir(d):
        raise IGError(f"pasta de mídia não existe: {d} (rode render_carousel.py)")
    names = sorted(f for f in os.listdir(d) if f.lower().endswith(".png"))
    if not names:
        raise IGError(f"nenhum PNG em {d}")
    if len(names) > 10:
        raise IGError(f"carrossel aceita no máximo 10 slides, achei {len(names)}")
    return [f"{base}/{post['media_dir'].replace(os.sep, '/')}/{n}" for n in names]


def create_child(ig_user_id: str, image_url: str, token: str) -> str:
    data = {"image_url": image_url, "is_carousel_item": "true", "access_token": token}
    res = _request("POST", f"{BASE}/{ig_user_id}/media", data)
    cid = res.get("id")
    if not cid:
        raise IGError(f"container filho sem id: {res}")
    return cid


def create_carousel(ig_user_id: str, children: list[str], caption: str, token: str) -> str:
    data = {
        "media_type": "CAROUSEL",
        "children": ",".join(children),
        "caption": caption,
        "access_token": token,
    }
    res = _request("POST", f"{BASE}/{ig_user_id}/media", data)
    cid = res.get("id")
    if not cid:
        raise IGError(f"container pai sem id: {res}")
    return cid


def pick(cfg: dict, args) -> dict | None:
    posts = cfg["posts"]
    if args.post:
        for p in posts:
            if p["id"] == args.post:
                return p
        raise IGError(f"post {args.post} não existe na agenda")
    today = date.today().isoformat()
    for p in posts:
        if p.get("date") == today:
            return p
    return None


def preflight(post: dict, urls: list[str]) -> None:
    """Checagens que falham BARATO, antes de gastar chamada de API."""
    if not post.get("approved"):
        raise IGError(
            f"post {post['id']} está approved=false — a aprovação do Caio é o gate "
            f"(edite automation/schedule.json via PR). Nada será publicado."
        )
    if post.get("published_at"):
        raise IGError(
            f"post {post['id']} já foi publicado em {post['published_at']} "
            f"({post.get('permalink')}). Recusando publicar de novo."
        )
    if not post.get("caption", "").strip():
        raise IGError(f"post {post['id']} sem caption")
    if len(post["caption"]) > 2200:
        raise IGError(f"caption do post {post['id']} tem {len(post['caption'])} chars (máx 2200)")


def cmd_list(cfg: dict) -> int:
    print(f"{'id':>3}  {'data':<12} {'apr':<4} {'estado':<28} título")
    for p in cfg["posts"]:
        st = f"publicado {p['published_at'][:10]}" if p.get("published_at") else "pendente"
        print(f"{p['id']:>3}  {p.get('date','-'):<12} {str(p.get('approved')):<4} {st:<28} {p['title']}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Publica carrossel no Instagram (API oficial).")
    ap.add_argument("--post", type=int, help="publicar este post da agenda")
    ap.add_argument("--due", action="store_true", help="publicar o agendado para hoje")
    ap.add_argument("--list", action="store_true", help="mostrar a agenda")
    ap.add_argument("--dry-run", action="store_true",
                    help="cria os containers e valida, mas NÃO publica")
    ap.add_argument("--ig-user-id", default=os.environ.get("IG_USER_ID"))
    ap.add_argument("--token", default=os.environ.get("IG_ACCESS_TOKEN"))
    a = ap.parse_args()

    cfg = load_schedule()
    if a.list:
        return cmd_list(cfg)
    if not (a.post or a.due):
        print("ERRO: use --post N, --due ou --list.", file=sys.stderr)
        return 2

    post = pick(cfg, a)
    if post is None:
        print(f"[due] nada agendado para {date.today().isoformat()} — nada a fazer.",
              file=sys.stderr)
        return 0

    urls = slide_urls(cfg, post)
    preflight(post, urls)
    print(f"[post {post['id']}] {post['title']} — {len(urls)} slides", file=sys.stderr)

    if not a.token:
        print("ERRO: defina IG_ACCESS_TOKEN (ou --token).", file=sys.stderr)
        return 2

    me = whoami(a.token)
    ig_user_id = a.ig_user_id or me.get("user_id")
    print(f"[whoami] @{me.get('username')} (user_id={ig_user_id})", file=sys.stderr)
    if not ig_user_id:
        print("ERRO: defina IG_USER_ID.", file=sys.stderr)
        return 2

    print(f"[1/4] criando {len(urls)} containers filhos...", file=sys.stderr)
    children = []
    for i, u in enumerate(urls, 1):
        cid = create_child(ig_user_id, u, a.token)
        children.append(cid)
        print(f"      slide {i}/{len(urls)} -> {cid}", file=sys.stderr)

    print("[2/4] criando container do carrossel...", file=sys.stderr)
    parent = create_carousel(ig_user_id, children, post["caption"], a.token)
    print(f"      carousel_id={parent}", file=sys.stderr)

    print("[3/4] aguardando FINISHED...", file=sys.stderr)
    wait_until_finished(parent, a.token)

    if a.dry_run:
        print("[dry-run] container FINISHED — publicação PULADA.", file=sys.stderr)
        print(json.dumps({"dry_run": True, "carousel_id": parent,
                          "children": children, "slides": urls}, indent=2))
        return 0

    print("[4/4] publicando...", file=sys.stderr)
    media_id = publish(ig_user_id, parent, a.token)
    link = permalink(media_id, a.token)

    # Marca como publicado no schedule — impede publicação dupla no próximo cron.
    post["published_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    post["permalink"] = link
    with open(SCHEDULE, "w", encoding="utf-8") as fh:
        json.dump(cfg, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    print(json.dumps({"media_id": media_id, "permalink": link}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except IGError as e:
        print(f"ERRO: {e}", file=sys.stderr)
        sys.exit(1)
