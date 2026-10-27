"""[FASE 2] Resumo diário do mercado escrito pelo Claude (API da Anthropic).

Já está pronto para uso. Para ligar:
  1. Crie uma chave em https://platform.claude.com (Settings > API keys).
  2. No GitHub: Settings > Secrets and variables > Actions > New repository
     secret. Nome: ANTHROPIC_API_KEY. Valor: a chave.
  3. Em requirements.txt, tire o "#" da linha `anthropic>=1.0`.
  4. Em config.yaml: modulos.resumo_ia.ativo = true
"""
from __future__ import annotations

import json
import logging

log = logging.getLogger(__name__)

INSTRUCOES = """Você é um analista do mercado de combustíveis que escreve para o \
dono de um posto de bandeira Ipiranga na Serra Gaúcha (RS). Com base nos \
indicadores e nas manchetes fornecidos, escreva um resumo em português do \
Brasil, em até 5 tópicos curtos, dizendo o que mudou, o que isso pode \
significar para o preço de compra nas distribuidoras nos próximos dias e o \
que vale acompanhar. Seja direto, sem jargão, e não invente números: use \
apenas os dados fornecidos. Se os dados forem insuficientes, diga isso."""


def gerar(config: dict, painel: dict) -> dict:
    import anthropic  # só é importado quando o módulo está ativo

    entrada = {
        "indicadores": painel["cartoes"],
        "manchetes": [
            {"titulo": n["titulo"], "fonte": n["fonte"], "data": n["publicado"][:10]}
            for n in painel["noticias"][:25]
        ],
    }
    client = anthropic.Anthropic()  # lê ANTHROPIC_API_KEY do ambiente
    resposta = client.beta.messages.create(
        model=config["modulos"]["resumo_ia"].get("modelo", "claude-opus-5-5"),
        max_tokens=4000,
        system=INSTRUCOES,
        messages=[{"role": "user", "content": json.dumps(entrada, ensure_ascii=False)}],
        # Se o modelo principal recusar, a API tenta automaticamente outro modelo.
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    )
    if resposta.stop_reason == "refusal":
        raise RuntimeError("O Claude recusou gerar o resumo hoje.")
    texto = "".join(b.text for b in resposta.content if b.type == "text").strip()
    return {"texto": texto, "modelo": resposta.model}
