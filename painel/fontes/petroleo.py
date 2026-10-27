"""Brent e WTI — fechamento diário em US$/barril.

Fonte principal: Yahoo Finance (contratos futuros BZ=F e CL=F) via
biblioteca yfinance, atualizada no mesmo dia. Reservas, em ordem: API de
gráficos do Yahoo acessada diretamente; FRED (Federal Reserve de St. Louis),
sem chave, mas que costuma vir com alguns dias de atraso.
"""
from __future__ import annotations

import io
import logging
import time
from datetime import date, datetime, timedelta, timezone

import pandas as pd
import requests

from painel import armazenamento

log = logging.getLogger(__name__)

SERIES = {
    # coluna: (ticker Yahoo, série FRED)
    "brent": ("BZ=F", "DCOILBRENTEU"),
    "wti": ("CL=F", "DCOILWTICO"),
}
NOME_ARQUIVO = "petroleo"


def _yahoo(ticker: str, inicio: date) -> pd.Series:
    import yfinance as yf

    df = yf.download(ticker, start=inicio.isoformat(), progress=False,
                     auto_adjust=False, threads=False)
    if df is None or df.empty:
        raise ValueError(f"Yahoo sem dados para {ticker}")
    fech = df["Close"]
    if isinstance(fech, pd.DataFrame):  # yfinance novo devolve colunas multinível
        fech = fech.iloc[:, 0]
    fech.index = pd.to_datetime(fech.index).tz_localize(None).normalize()
    return fech.dropna()


def _yahoo_direto(ticker: str, inicio: date) -> pd.Series:
    inicio_ts = int(datetime.combine(inicio, datetime.min.time(), timezone.utc).timestamp())
    r = requests.get(
        f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}",
        params={"period1": inicio_ts, "period2": int(time.time()), "interval": "1d"},
        headers={"User-Agent": "Mozilla/5.0"}, timeout=30,
    )
    r.raise_for_status()
    res = r.json()["chart"]["result"][0]
    datas = pd.to_datetime(res["timestamp"], unit="s").normalize()
    s = pd.Series(res["indicators"]["quote"][0]["close"], index=datas, dtype="float64")
    return s[~s.index.duplicated(keep="last")].dropna()


def _fred(serie: str, inicio: date) -> pd.Series:
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={serie}&cosd={inicio.isoformat()}"
    r = requests.get(url, timeout=30, headers={"User-Agent": "painel-combustiveis"})
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text))
    df.columns = ["data", "valor"]
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    df = df.dropna()
    return pd.Series(df["valor"].values, index=pd.to_datetime(df["data"]))


def _buscar(coluna: str, inicio: date) -> pd.Series:
    ticker, fred = SERIES[coluna]
    tentativas = [("yfinance", lambda: _yahoo(ticker, inicio)),
                  ("Yahoo direto", lambda: _yahoo_direto(ticker, inicio)),
                  ("FRED", lambda: _fred(fred, inicio))]
    erros = []
    for nome, buscar in tentativas:
        try:
            return buscar()
        except Exception as e:  # noqa: BLE001
            log.warning("%s falhou para %s: %s", nome, coluna, e)
            erros.append(f"{nome}: {e}")
    raise RuntimeError(f"todas as fontes falharam para {coluna} ({'; '.join(erros)})")


def coletar(config: dict) -> dict:
    ultima = armazenamento.ultima_data(NOME_ARQUIVO)
    if ultima is None:
        inicio = date.today() - timedelta(days=config["historico"]["dias_iniciais"])
    else:
        # Rebusca alguns dias para corrigir fechamentos revisados.
        inicio = ultima.date() - timedelta(days=10)

    novos = pd.DataFrame({c: _buscar(c, inicio) for c in SERIES})
    novos.index.name = "data"
    df = armazenamento.salvar_serie(NOME_ARQUIVO, novos.reset_index())
    log.info("Petróleo: %d linhas no histórico (até %s)", len(df), df["data"].max().date())
    return {"df": df}
