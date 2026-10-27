"""Dólar PTAX (venda) — API SGS do Banco Central, série 1.

Documentação: https://dadosabertos.bcb.gov.br/dataset/dolar-americano-usd-todos-os-boletins-diarios
A API SGS limita consultas diárias a 10 anos por chamada.
"""
from __future__ import annotations

import logging
from datetime import date, timedelta

import pandas as pd
import requests

from painel import armazenamento

log = logging.getLogger(__name__)

SERIE_SGS = 1  # Dólar americano (venda) — PTAX
URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{serie}/dados"
NOME_ARQUIVO = "ptax"


def coletar(config: dict) -> dict:
    ultima = armazenamento.ultima_data(NOME_ARQUIVO)
    if ultima is None:
        inicio = date.today() - timedelta(days=config["historico"]["dias_iniciais"])
    else:
        inicio = ultima.date() - timedelta(days=7)

    params = {
        "formato": "json",
        "dataInicial": inicio.strftime("%d/%m/%Y"),
        "dataFinal": date.today().strftime("%d/%m/%Y"),
    }
    r = requests.get(URL.format(serie=SERIE_SGS), params=params, timeout=30)
    r.raise_for_status()
    dados = r.json()
    if not dados:
        raise ValueError("SGS/BCB devolveu lista vazia")

    novos = pd.DataFrame(dados)
    novos["data"] = pd.to_datetime(novos["data"], format="%d/%m/%Y")
    novos["ptax"] = pd.to_numeric(novos["valor"])
    df = armazenamento.salvar_serie(NOME_ARQUIVO, novos[["data", "ptax"]])
    log.info("PTAX: %d linhas no histórico (até %s)", len(df), df["data"].max().date())
    return {"df": df}
