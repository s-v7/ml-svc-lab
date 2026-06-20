"""
    Narra resultados de experimentos em prosa....

    Princípio herdado do grafos_municipios_br: os NÚMEROS vem prontos
    (calculados pelos modelos); LLM apenas DESCREVE.
    Nunca recalcula, nunca inventa métricas.

    Uso (programático):
        from integration.narrator import narra
        text = narra(resultados_dict, provider="opeanai")
"""
from __future__ import annotations

from integration.clients import LLMClient, get_client
import json

SYSTEM = (
    "Você resume resultados de experimentos de Machine Learning em português,"
    "de forma honesta e técnica. Use SOMENTE os números fornecidos no JSON."
    "NUNCA invente métricas nem recalcule nada. Seja conciso (3-4 frase)."
)

def narra(resultados: dict, client: LLMClient | None = None, provider: str = "echo") -> str:
    client = client or get_client(provider)
    prompt = ("Resuma os resultados abaixo, dizendo quais os modelos bateram o baseline e o "
              "que isso significa na prática. Não invente números.\n\n"
            + json.dumps(resultados, ensure_ascii=False, indent=2)
    )
    return client.complete(prompt, system=SYSTEM)

