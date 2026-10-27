"""Dólar PTAX (venda) — Banco Central.

Fonte principal: API SGS, série 1.
  https://dadosabertos.bcb.gov.br/dataset/dolar-americano-usd-todos-os-boletins-diarios
Reserva: API PTAX (Olinda), que traz a mesma cotação de fechamento.
  https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/aplicacao
A SGS costuma responder com erro 502 por alguns minutos; por isso cada
API é tentada mais de uma vez antes de passar para a próxima.
"""
from __future__ import annotations

import logging
import time
from datetime import date, timedelta

import pandas as pd
import requests

from painel import armazenamento

log = logging.getLogger(__name__)

SERIE_SGS = 1  # Dólar americano (venda) — PTAX
URL_SGS = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{serie}/dados"
URL_OLINDA = ("https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/"
              "CotacaoDolarPeriodo(dataInicial=@i,dataFinalCotacao=@f)")
NOME_ARQUIVO = "ptax"
TENTATIVAS = 3
ESPERA_SEGUNDOS = 10


def _get_json(url: str, params: dict):
    r = requests.get(url, params=params, timeout=60,
                     headers={"Accept": "application/json"})
    r.raise_for_status()
    return r.json()


def _sgs(inicio: date, fim: date) -> pd.DataFrame:
    dados = _get_json(URL_SGS.format(serie=SERIE_SGS), {
        "formato": "json",
        "dataInicial": inicio.strftime("%d/%m/%Y"),
        "dataFinal": fim.strftime("%d/%m/%Y"),
    })
    df = pd.DataFrame(dados)
    df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
    df["ptax"] = pd.to_numeric(df["valor"])
    return df[["data", "ptax"]]


def _olinda(inicio: date, fim: date) -> pd.DataFrame:
    dados = _get_json(URL_OLINDA, {
        "@i": f"'{inicio:%m-%d-%Y}'",
        "@f": f"'{fim:%m-%d-%Y}'",
        "$format": "json",
        "$select": "cotacaoVenda,dataHoraCotacao",
    })["value"]
    df = pd.DataFrame(dados)
    df["data"] = pd.to_datetime(df["dataHoraCotacao"]).dt.normalize()
    df["ptax"] = pd.to_numeric(df["cotacaoVenda"])
    # Uma cotação de fechamento por dia; se vier mais de uma, fica a última.
    return df.sort_values("dataHoraCotacao").drop_duplicates("data", keep="last")[["data", "ptax"]]


def _buscar(inicio: date, fim: date) -> pd.DataFrame:
    erros = []
    for nome, buscar in (("SGS", _sgs), ("Olinda", _olinda)):
        for tentativa in range(1, TENTATIVAS + 1):
            try:
                df = buscar(inicio, fim)
                if df.empty:
                    raise ValueError("resposta sem dados")
                if nome != "SGS":
                    log.warning("PTAX obtida pela API reserva (%s)", nome)
                return df
            except Exception as e:  # noqa: BLE001
                log.warning("PTAX %s, tentativa %d/%d: %s", nome, tentativa, TENTATIVAS, e)
                erros.append(f"{nome}: {e}")
                if tentativa < TENTATIVAS:
                    time.sleep(ESPERA_SEGUNDOS)
    raise RuntimeError("APIs do Banco Central indisponíveis (" + erros[-1] + ")")


def coletar(config: dict) -> dict:
    ultima = armazenamento.ultima_data(NOME_ARQUIVO)
    if ultima is None:
        inicio = date.today() - timedelta(days=config["historico"]["dias_iniciais"])
    else:
        inicio = ultima.date() - timedelta(days=7)

    novos = _buscar(inicio, date.today())
    df = armazenamento.salvar_serie(NOME_ARQUIVO, novos)
    log.info("PTAX: %d linhas no histórico (até %s)", len(df), df["data"].max().date())
    return {"df": df}
