"""[FASE 2] Defasagem de preços — Abicom.

A Abicom publica diariamente a defasagem média entre o preço da Petrobras
nas refinarias e o preço de paridade de importação (PPI), para gasolina
e diesel, em R$/litro e em %.

Como implementar:
  - Ver em https://abicom.com.br/categoria/ppi/ onde o número é publicado
    (o relatório costuma sair como post/imagem/PDF; pode ser preciso ler
    o texto do post com requests + BeautifulSoup).
  - Gravar com armazenamento.salvar_serie("abicom", df) com colunas
    data, gasolina_rs, gasolina_pct, diesel_rs, diesel_pct.
  - Devolver {"df": df} e criar templates/secoes/abicom.html.j2.
  - Ligar em config.yaml: modulos.abicom.ativo = true
"""
from __future__ import annotations


def coletar(config: dict) -> dict:
    raise NotImplementedError("Módulo Abicom ainda não implementado (Fase 2).")
