"""Análises: rodam DEPOIS das fontes e dos indicadores.

Contrato:

    def gerar(config: dict, painel: dict) -> dict

`painel` contém tudo o que a página vai mostrar (indicadores, notícias,
resultados das fontes). O dicionário devolvido fica disponível no
template como `analises.<nome_do_modulo>`.
"""

ORDEM = [
    "resumo_ia",
]
