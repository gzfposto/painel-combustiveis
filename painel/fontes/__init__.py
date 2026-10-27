"""Fontes de dados do painel.

Cada módulo desta pasta segue o mesmo contrato:

    def coletar(config: dict) -> dict

- Busca os dados na internet, grava o histórico em dados/ (via
  painel.armazenamento) e devolve um dicionário com o que a página precisa.
- O dicionário devolvido fica disponível no template como
  `fontes.<nome_do_modulo>`.
- Se algo falhar, levante uma exceção: o main.py registra o erro, mostra
  um aviso na página e continua com as outras fontes.

Para criar uma fonte nova:
  1. crie painel/fontes/<nome>.py com a função coletar(config);
  2. acrescente o nome em ORDEM abaixo;
  3. ligue-a em config.yaml (modulos: <nome>: {ativo: true});
  4. (opcional) crie painel/templates/secoes/<nome>.html.j2 para exibi-la.
"""

# Ordem de execução.
ORDEM = [
    "petroleo",
    "ptax",
    "noticias",
    "abicom",
    "anp",
    "cepea",
]
