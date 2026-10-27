"""[FASE 2] Indicadores CEPEA/Esalq de etanol (hidratado e anidro).

Como implementar:
  - Página: https://www.cepea.org.br/br/indicador/etanol.aspx
    (há tabela HTML com os últimos valores e link de download .xls).
  - Ler com pandas.read_html ou baixar a planilha da série histórica.
  - Gravar com armazenamento.salvar_serie("cepea_etanol", df) com colunas
    data, hidratado, anidro (R$/litro).
  - Devolver {"df": df} e criar templates/secoes/cepea.html.j2.
  - Ligar em config.yaml: modulos.cepea.ativo = true
"""
from __future__ import annotations


def coletar(config: dict) -> dict:
    raise NotImplementedError("Módulo CEPEA ainda não implementado (Fase 2).")
