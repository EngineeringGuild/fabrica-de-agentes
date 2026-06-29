#!/usr/bin/env python3
"""
publish_instagram.py — Publica uma imagem no Instagram via API oficial.

Usa a **Instagram API with Instagram Login** (graph.instagram.com), que permite
contas Creator publicarem SEM Página do Facebook. Fluxo de 2 passos (container):

    1) POST /{ig_user_id}/media          -> cria o container (image_url + caption)
    2) (poll) GET /{container_id}?fields=status_code  -> espera FINISHED
    3) POST /{ig_user_id}/media_publish  -> publica (creation_id = container_id)

Também faz refresh do token long-lived (60 dias) quando perto de expirar.

Sem dependências externas — só a stdlib (funciona no runner do GitHub Actions e
local sem `pip install`). Python 3.9+ (na máquina: usar `python`/`py`, nunca `python3`).

Variáveis de ambiente (ou flags):
    IG_USER_ID        ID numérico da conta Instagram (Creator)
    IG_ACCESS_TOKEN   token long-lived com escopo instagram_content_publish
    GRAPH_HOST        default: graph.instagram.com  (IG Login API)
    GRAPH_VERSION     default: v23.0

Exemplos:
    python publish_instagram.py --image-url https://.../post.jpg --caption-file cap.txt --dry-run
    python publish_instagram.py --image-url https://.../post.jpg --caption "texto..."
    python publish_instagram.py --refresh-token            # só renova o token e imprime o novo
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

GRAPH_HOST = os.environ.get("GRAPH_HOST", "graph.instagram.com")
GRAPH_VERSION = os.environ.get("GRAPH_VERSION", "v23.0")
BASE = f"https://{GRAPH_HOST}/{GRAPH_VERSION}"

# Container pode demorar para processar a imagem. Poll com backoff.
CONTAINER_POLL_MAX_TRIES = 20
CONTAINER_POLL_INTERVAL = 3  # segundos (cresce levemente)


class IGError(RuntimeError):
    pass


def _request(method: str, url: str, data: dict | None = None, *, tries: int = 4) -> dict:
    """HTTP com tratamento de 429 (backoff exponencial) e erros da Graph API."""
    body = urllib.parse.urlencode(data).encode() if data else None
    for attempt in range(1, tries + 1):
        req = urllib.request.Request(url, data=body, method=method)
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                raw = resp.read().decode()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            raw = e.read().decode()
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                payload = {"error": {"message": raw}}
            # 429 / rate limit -> backoff e retry
            if e.code == 429 and attempt < tries:
                wait = 2 ** attempt
                print(f"[rate-limit] 429; aguardando {wait}s (tentativa {attempt}/{tries})", file=sys.stderr)
                time.sleep(wait)
                continue
            msg = payload.get("error", {}).get("message", raw)
            raise IGError(f"HTTP {e.code} em {method} {url}: {msg}") from e
        except urllib.error.URLError as e:
            if attempt < tries:
                wait = 2 ** attempt
                print(f"[net] {e}; retry em {wait}s", file=sys.stderr)
                time.sleep(wait)
                continue
            raise IGError(f"Falha de rede em {method} {url}: {e}") from e
    raise IGError("esgotou tentativas")  # pragma: no cover


def whoami(token: str) -> dict:
    """Valida o token: retorna user_id + username da conta."""
    qs = urllib.parse.urlencode({"fields": "user_id,username", "access_token": token})
    return _request("GET", f"{BASE}/me?{qs}")


def create_container(ig_user_id: str, image_url: str, caption: str, token: str) -> str:
    data = {"image_url": image_url, "caption": caption, "access_token": token}
    res = _request("POST", f"{BASE}/{ig_user_id}/media", data)
    cid = res.get("id")
    if not cid:
        raise IGError(f"container sem id: {res}")
    return cid


def wait_until_finished(container_id: str, token: str) -> None:
    qs = urllib.parse.urlencode({"fields": "status_code,status", "access_token": token})
    for i in range(1, CONTAINER_POLL_MAX_TRIES + 1):
        res = _request("GET", f"{BASE}/{container_id}?{qs}")
        status = res.get("status_code")
        if status == "FINISHED":
            return
        if status == "ERROR":
            raise IGError(f"container em ERROR: {res.get('status')}")
        print(f"[container] status={status} ({i}/{CONTAINER_POLL_MAX_TRIES})", file=sys.stderr)
        time.sleep(CONTAINER_POLL_INTERVAL + i)  # backoff suave
    raise IGError("container não ficou FINISHED a tempo")


def publish(ig_user_id: str, container_id: str, token: str) -> str:
    data = {"creation_id": container_id, "access_token": token}
    res = _request("POST", f"{BASE}/{ig_user_id}/media_publish", data)
    media_id = res.get("id")
    if not media_id:
        raise IGError(f"publish sem id: {res}")
    return media_id


def permalink(media_id: str, token: str) -> str | None:
    qs = urllib.parse.urlencode({"fields": "permalink", "access_token": token})
    try:
        return _request("GET", f"{BASE}/{media_id}?{qs}").get("permalink")
    except IGError:
        return None


def refresh_token(token: str) -> dict:
    """Renova o token long-lived (ig_refresh_token). Retorna novo token + expires_in."""
    qs = urllib.parse.urlencode({"grant_type": "ig_refresh_token", "access_token": token})
    return _request("GET", f"{BASE}/refresh_access_token?{qs}")


def main() -> int:
    p = argparse.ArgumentParser(description="Publica imagem no Instagram (API oficial).")
    p.add_argument("--image-url", help="URL pública da imagem (requisito da API).")
    p.add_argument("--caption", help="Legenda (texto direto).")
    p.add_argument("--caption-file", help="Arquivo com a legenda (UTF-8).")
    p.add_argument("--ig-user-id", default=os.environ.get("IG_USER_ID"))
    p.add_argument("--token", default=os.environ.get("IG_ACCESS_TOKEN"))
    p.add_argument("--dry-run", action="store_true",
                   help="Cria o container e valida FINISHED, mas NÃO publica.")
    p.add_argument("--refresh-token", action="store_true",
                   help="Apenas renova o token long-lived e imprime o novo.")
    args = p.parse_args()

    token = args.token
    if not token:
        print("ERRO: defina IG_ACCESS_TOKEN (ou --token).", file=sys.stderr)
        return 2

    if args.refresh_token:
        res = refresh_token(token)
        print(json.dumps(res, indent=2))
        return 0

    # Validação de identidade (sempre — barato e prova que o token funciona)
    me = whoami(token)
    print(f"[whoami] @{me.get('username')} (user_id={me.get('user_id')})", file=sys.stderr)

    if not args.image_url:
        print("ERRO: --image-url é obrigatório para publicar.", file=sys.stderr)
        return 2

    caption = args.caption or ""
    if args.caption_file:
        with open(args.caption_file, encoding="utf-8") as fh:
            caption = fh.read()

    ig_user_id = args.ig_user_id or me.get("user_id")
    if not ig_user_id:
        print("ERRO: defina IG_USER_ID (ou --ig-user-id).", file=sys.stderr)
        return 2

    print("[1/3] criando container...", file=sys.stderr)
    cid = create_container(ig_user_id, args.image_url, caption, token)
    print(f"      container_id={cid}", file=sys.stderr)

    print("[2/3] aguardando processamento (FINISHED)...", file=sys.stderr)
    wait_until_finished(cid, token)

    if args.dry_run:
        print("[dry-run] container FINISHED — publicação PULADA.", file=sys.stderr)
        print(json.dumps({"dry_run": True, "container_id": cid}, indent=2))
        return 0

    print("[3/3] publicando...", file=sys.stderr)
    media_id = publish(ig_user_id, cid, token)
    link = permalink(media_id, token)
    out = {"media_id": media_id, "permalink": link}
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
