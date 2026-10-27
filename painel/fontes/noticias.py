"""Notícias via RSS do Google News, sem duplicatas, últimos N dias.

As notícias coletadas são acumuladas em dados/noticias.json, para que a
página continue mostrando a semana inteira mesmo que o Google mude o que
aparece no feed entre uma execução e outra.
"""
from __future__ import annotations

import logging
import re
import unicodedata
from datetime import datetime, timedelta, timezone
from urllib.parse import quote_plus

import feedparser

from painel import armazenamento

log = logging.getLogger(__name__)

URL = "https://news.google.com/rss/search?q={q}+when:{dias}d&hl=pt-BR&gl=BR&ceid=BR:pt-419"
NOME_ARQUIVO = "noticias"


def _chave(titulo: str) -> str:
    """Chave para detectar duplicatas: sem acento, sem pontuação, minúsculas."""
    t = unicodedata.normalize("NFKD", titulo).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-z0-9 ]", " ", t.lower())
    return " ".join(t.split())[:90]


def _separar_fonte(titulo: str, fonte: str) -> str:
    """O Google News acrescenta ' - Nome do Veículo' ao final do título."""
    sufixo = f" - {fonte}"
    return titulo[: -len(sufixo)] if fonte and titulo.endswith(sufixo) else titulo


def _buscar_termo(termo: str, dias: int, limite: int) -> list[dict]:
    feed = feedparser.parse(URL.format(q=quote_plus(termo), dias=dias))
    itens = []
    for e in feed.entries[:limite]:
        if not getattr(e, "published_parsed", None):
            continue
        fonte = getattr(getattr(e, "source", None), "title", "") or ""
        itens.append({
            "titulo": _separar_fonte(e.title, fonte),
            "link": e.link,
            "fonte": fonte,
            "publicado": datetime(*e.published_parsed[:6], tzinfo=timezone.utc).isoformat(),
            "termo": termo,
        })
    return itens


def coletar(config: dict) -> dict:
    cfg = config["noticias"]
    dias = cfg["dias"]
    corte = datetime.now(timezone.utc) - timedelta(days=dias)

    anteriores = armazenamento.ler_json(NOME_ARQUIVO, padrao=[])
    novas = []
    for termo in cfg["termos"]:
        try:
            novas += _buscar_termo(termo, dias, cfg["max_por_termo"])
        except Exception as e:  # noqa: BLE001
            log.warning("RSS falhou para '%s': %s", termo, e)

    unicas: dict[str, dict] = {}
    for n in novas + anteriores:  # novas primeiro: em caso de empate, ficam
        if datetime.fromisoformat(n["publicado"]) < corte:
            continue
        unicas.setdefault(_chave(n["titulo"]), n)

    lista = sorted(unicas.values(), key=lambda n: n["publicado"], reverse=True)
    lista = lista[: cfg["max_total"]]
    armazenamento.salvar_json(NOME_ARQUIVO, lista)
    log.info("Notícias: %d únicas nos últimos %d dias", len(lista), dias)
    return {"itens": lista}
