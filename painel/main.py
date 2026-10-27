"""Ponto de entrada: coleta tudo, calcula e gera site/index.html.

Uso (o GitHub Actions roda exatamente isto):
    python -m painel.main
"""
from __future__ import annotations

import importlib
import logging
import shutil
from datetime import datetime
from zoneinfo import ZoneInfo

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

from painel import analises, armazenamento, fontes, indicadores

log = logging.getLogger("painel")
RAIZ = armazenamento.RAIZ
SITE = RAIZ / "site"
TEMPLATES = RAIZ / "painel" / "templates"
FUSO = ZoneInfo("America/Sao_Paulo")


def carregar_config() -> dict:
    return yaml.safe_load((RAIZ / "config.yaml").read_text(encoding="utf-8"))


def ativo(config: dict, nome: str) -> bool:
    return bool(config.get("modulos", {}).get(nome, {}).get("ativo", False))


def rodar_modulos(pacote, ordem, config, funcao, *args) -> tuple[dict, list[str]]:
    """Executa cada módulo ativo; uma falha não derruba os demais."""
    resultados, avisos = {}, []
    for nome in ordem:
        if not ativo(config, nome):
            continue
        try:
            mod = importlib.import_module(f"{pacote.__name__}.{nome}")
            resultados[nome] = getattr(mod, funcao)(config, *args)
        except Exception as e:  # noqa: BLE001
            log.exception("Falha no módulo %s", nome)
            avisos.append(f"{nome}: {e}")
    return resultados, avisos


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    config = carregar_config()
    g = config["graficos"]
    curta, longa = g["media_curta"], g["media_longa"]

    res, avisos = rodar_modulos(fontes, fontes.ORDEM, config, "coletar")

    # Se uma fonte falhar hoje, a página usa o histórico já salvo.
    petroleo = res.get("petroleo", {}).get("df")
    if petroleo is None:
        petroleo = armazenamento.ler_serie("petroleo")
    ptax = res.get("ptax", {}).get("df")
    if ptax is None:
        ptax = armazenamento.ler_serie("ptax")
    brl = None
    if not petroleo.empty and not ptax.empty:
        brl = indicadores.juntar_brent_ptax(petroleo, ptax, curta, longa)
        armazenamento.salvar_serie("brent_brl", brl)

    painel = {
        "posto": config["posto"],
        "atualizado": datetime.now(FUSO).strftime("%d/%m/%Y às %H:%M"),
        "cartoes": indicadores.montar_cartoes(petroleo, ptax, brl, curta, longa),
        "graficos": {
            "brl": indicadores.series_para_grafico(
                brl, ["brent_brl", f"mm{curta}", f"mm{longa}"], g["dias_exibidos"]),
            "usd": indicadores.series_para_grafico(
                petroleo, ["brent", "wti"], g["dias_exibidos"]),
            "ptax": indicadores.series_para_grafico(ptax, ["ptax"], g["dias_exibidos"]),
        },
        "curta": curta,
        "longa": longa,
        "noticias": res.get("noticias", {}).get("itens")
                    or armazenamento.ler_json("noticias", padrao=[]),
        "dias_noticias": config["noticias"]["dias"],
        "fontes": res,
    }

    res_an, avisos_an = rodar_modulos(analises, analises.ORDEM, config, "gerar", painel)
    painel["analises"] = res_an
    painel["avisos"] = avisos + avisos_an

    # Seções extras: qualquer módulo ativo com templates/secoes/<nome>.html.j2
    painel["secoes_extras"] = [
        n for n in fontes.ORDEM + analises.ORDEM
        if n in res or n in res_an
        if (TEMPLATES / "secoes" / f"{n}.html.j2").exists()
    ]

    gerar_site(painel)


def gerar_site(painel: dict) -> None:
    env = Environment(loader=FileSystemLoader(TEMPLATES),
                      autoescape=select_autoescape(["html", "j2"]))
    env.filters["num"] = lambda v, casas=2: (
        "—" if v is None else f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", "."))
    env.filters["pct"] = lambda v: (
        "—" if v is None else f"{v:+.2f}%".replace(".", ","))

    SITE.mkdir(exist_ok=True)
    html = env.get_template("index.html.j2").render(**painel)
    (SITE / "index.html").write_text(html, encoding="utf-8")
    # Publica também os CSVs, para download direto pela página.
    destino = SITE / "dados"
    shutil.rmtree(destino, ignore_errors=True)
    shutil.copytree(armazenamento.DADOS, destino)
    log.info("Página gerada em %s", SITE / "index.html")


if __name__ == "__main__":
    main()
