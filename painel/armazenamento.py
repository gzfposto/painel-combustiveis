"""Leitura e gravação do histórico em CSV (pasta dados/).

Cada série é um CSV simples com colunas `data,<colunas...>`, legível no
Excel e no próprio GitHub. Novos dados são mesclados ao histórico: a
mesma data nunca aparece duas vezes (o valor mais novo prevalece).
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
DADOS = RAIZ / "dados"


def _datas(col: pd.Series) -> pd.Series:
    """Datas sempre no mesmo formato (o pandas 3 varia a precisão conforme a
    origem, e séries com precisões diferentes não podem ser combinadas)."""
    return pd.to_datetime(col).dt.normalize().astype("datetime64[ns]")


def caminho(nome: str) -> Path:
    DADOS.mkdir(exist_ok=True)
    return DADOS / nome


def ler_serie(nome: str) -> pd.DataFrame:
    """Lê dados/<nome>.csv. Retorna DataFrame vazio se não existir."""
    arq = caminho(f"{nome}.csv")
    if not arq.exists():
        return pd.DataFrame()
    df = pd.read_csv(arq)
    df["data"] = _datas(df["data"])
    return df.sort_values("data").reset_index(drop=True)


def salvar_serie(nome: str, novos: pd.DataFrame) -> pd.DataFrame:
    """Mescla `novos` ao histórico existente e grava. Retorna o resultado."""
    if novos is None or novos.empty:
        return ler_serie(nome)
    antigo = ler_serie(nome)
    novos = novos.copy()
    novos["data"] = _datas(novos["data"])
    df = pd.concat([antigo, novos], ignore_index=True)
    df = df.drop_duplicates(subset="data", keep="last").sort_values("data")
    df.to_csv(caminho(f"{nome}.csv"), index=False, date_format="%Y-%m-%d",
              float_format="%.4f")
    return df.reset_index(drop=True)


def ultima_data(nome: str):
    df = ler_serie(nome)
    return None if df.empty else df["data"].max()


def ler_json(nome: str, padrao=None):
    arq = caminho(f"{nome}.json")
    if not arq.exists():
        return padrao
    return json.loads(arq.read_text(encoding="utf-8"))


def salvar_json(nome: str, conteudo) -> None:
    caminho(f"{nome}.json").write_text(
        json.dumps(conteudo, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
