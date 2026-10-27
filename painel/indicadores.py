"""Cálculos: Brent em reais, médias móveis e variações (dia/semana/mês)."""
from __future__ import annotations

import math
from datetime import timedelta

import pandas as pd

LITROS_POR_BARRIL = 158.987


def juntar_brent_ptax(petroleo: pd.DataFrame, ptax: pd.DataFrame,
                      curta: int, longa: int) -> pd.DataFrame:
    """Converte o Brent para reais usando a PTAX do mesmo dia (ou a última
    disponível antes dele, em feriados brasileiros) e calcula as médias."""
    p = petroleo.dropna(subset=["brent"]).sort_values("data")
    d = ptax.dropna(subset=["ptax"]).sort_values("data")
    df = pd.merge_asof(p, d, on="data", direction="backward").dropna(subset=["ptax"])
    df["brent_brl"] = df["brent"] * df["ptax"]
    df["brent_brl_litro"] = df["brent_brl"] / LITROS_POR_BARRIL
    df[f"mm{curta}"] = df["brent_brl"].rolling(curta).mean()
    df[f"mm{longa}"] = df["brent_brl"].rolling(longa).mean()
    return df.reset_index(drop=True)


def _valor_em(s: pd.Series, limite) -> float | None:
    """Último valor da série em ou antes da data `limite`."""
    anteriores = s[s.index <= limite]
    return None if anteriores.empty else float(anteriores.iloc[-1])


def _pct(atual: float, antes: float | None) -> float | None:
    if antes is None or antes == 0 or math.isnan(antes):
        return None
    return (atual / antes - 1) * 100


def variacoes(df: pd.DataFrame, coluna: str) -> dict:
    s = df.set_index("data")[coluna].dropna()
    if len(s) < 2:
        return {}
    data, atual = s.index[-1], float(s.iloc[-1])
    return {
        "valor": atual,
        "data": data.strftime("%d/%m/%Y"),
        "dia": _pct(atual, float(s.iloc[-2])),
        "semana": _pct(atual, _valor_em(s, data - timedelta(days=7))),
        "mes": _pct(atual, _valor_em(s, data - timedelta(days=30))),
    }


def montar_cartoes(petroleo: pd.DataFrame | None, ptax: pd.DataFrame | None,
                   brl: pd.DataFrame | None, curta: int, longa: int) -> list[dict]:
    cartoes = []

    def add(titulo, unidade, casas, df, coluna, extra=None):
        if df is None or df.empty or coluna not in df:
            return
        v = variacoes(df, coluna)
        if v:
            cartoes.append({"titulo": titulo, "unidade": unidade, "casas": casas,
                            **v, **(extra or {})})

    add("Brent", "US$/barril", 2, petroleo, "brent")
    add("WTI", "US$/barril", 2, petroleo, "wti")
    add("Dólar PTAX", "R$/US$", 4, ptax, "ptax")

    if brl is not None and not brl.empty:
        ult = brl.iloc[-1]
        sinais = []
        for n in (curta, longa):
            mm = ult.get(f"mm{n}")
            if pd.notna(mm):
                sinais.append({"rotulo": f"MM{n}", "valor": float(mm),
                               "acima": bool(ult["brent_brl"] > mm)})
        add("Brent em reais", "R$/barril", 2, brl, "brent_brl", {"medias": sinais})
        add("Brent em reais por litro", "R$/litro", 4, brl, "brent_brl_litro")
    return cartoes


def series_para_grafico(df: pd.DataFrame | None, colunas: list[str], dias: int) -> dict:
    """Recorta os últimos `dias` e converte para listas (JSON) do Chart.js."""
    if df is None or df.empty:
        return {"datas": []}
    corte = df["data"].max() - timedelta(days=dias)
    rec = df[df["data"] >= corte]
    saida = {"datas": rec["data"].dt.strftime("%d/%m/%y").tolist()}
    for c in colunas:
        if c in rec:
            saida[c] = [None if pd.isna(x) else round(float(x), 4) for x in rec[c]]
    return saida
