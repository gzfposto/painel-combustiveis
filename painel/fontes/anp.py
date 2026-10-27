"""[FASE 2] Preços semanais da ANP por município (Levantamento de Preços).

A ANP publica toda semana uma planilha com preço médio, mínimo e máximo
por município e produto (gasolina comum, etanol, diesel S10...).

Como implementar:
  - Página: https://www.gov.br/anp/pt-br/assuntos/precos-e-defesa-da-concorrencia/precos/levantamento-de-precos-de-combustiveis-ultimas-semanas-pesquisadas
  - Baixar o .xlsx "semanal - municípios" mais recente (pandas.read_excel,
    precisa acrescentar `openpyxl` em requirements.txt).
  - Filtrar por config["posto"]["uf"] e config["posto"]["cidade"]
    (e, se quiser, cidades vizinhas: Bento Gonçalves, Farroupilha...).
  - Gravar com armazenamento.salvar_serie("anp_<cidade>", df).
  - Devolver {"df": df} e criar templates/secoes/anp.html.j2.
  - Ligar em config.yaml: modulos.anp.ativo = true
"""
from __future__ import annotations


def coletar(config: dict) -> dict:
    raise NotImplementedError("Módulo ANP ainda não implementado (Fase 2).")
