"""
llm_forecaster.py - LLM como PREVISOR (baseline competidor) para a temperatura.

Da ao LLM os ultimos W dias e pede a temperatura media de amanha; coleta as
previsoes e avalia com common.metrics, comparando com a persistencia — no MESMO
conjunto de teste temporal.

Honestidade: LLMs sao reconhecidamente fracos em series temporais numericas; o
objetivo aqui e MEDIR isso com rigor, nao vencer. So usamos historico ANTERIOR
ao alvo (sem vazamento). Para nao gastar muitas chamadas, --n limita aos ultimos
N dias do teste.

Uso:
  PYTHONPATH=. python3 -m experiments.weather.llm_forecaster --provider echo --n 20
  PYTHONPATH=. python3 -m experiments.weather.llm_forecaster --provider openai --n 30
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
from common.data import load_table        # noqa: E402
from common.splits import temporal_split  # noqa: E402
from common.metrics import regression_metrics  # noqa: E402
from integration.clients import get_client  # noqa: E402

DADOS = "experiments/weather/data/weather_teresina.csv"
SYSTEM = ("Voce e um previsor de temperatura. Responda APENAS com um numero "
          "(graus Celsius), a temperatura media prevista para o dia seguinte. "
          "Sem texto, sem unidade, so o numero.")


def _num(texto: str) -> float | None:
    m = re.search(r"[-+]?\d+(?:[.,]\d+)?", texto)
    return float(m.group().replace(",", ".")) if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", default="echo",
                    choices=["echo", "openai", "anthropic", "nvidia"])
    ap.add_argument("--n", type=int, default=20, help="ultimos N dias do teste")
    ap.add_argument("--janela", type=int, default=14, help="dias de histórico no prompt")
    a = ap.parse_args()

    df = load_table(DADOS).copy()
    df["data"] = __import__("pandas").to_datetime(df["data"])
    df = df.sort_values("data").reset_index(drop=True)
    temp = df["temperature_2m_mean"].to_numpy(dtype=float)
    datas = df["data"].dt.strftime("%Y-%m-%d").to_numpy()

    n = len(temp) - 1                       # ultimo dia nao tem "amanha"
    _, _, te = temporal_split(n)
    alvos = te[-a.n:]                        # ultimos N indices de teste

    # echo offline devolve a persistencia (temp de hoje) para validar o pipeline
    client = get_client(a.provider, resposta="") if a.provider == "echo" \
        else get_client(a.provider)

    y_true, y_llm, y_persist = [], [], []
    for t in alvos:
        ini = max(0, t - a.janela)
        hist = "\n".join(f"{datas[i]}: {temp[i]:.1f}" for i in range(ini, t + 1))
        prompt = (f"Histórico de temperatura média diária (C):\n{hist}\n\n"
                  f"Qual a temperatura média de {datas[t + 1]}? Responda so o numero.")
        if a.provider == "echo":
            resp = f"{temp[t]:.1f}"          # stub = persistencia
        else:
            resp = client.complete(prompt, system=SYSTEM)
        pred = _num(resp)
        if pred is None:
            continue
        y_true.append(temp[t + 1])
        y_llm.append(pred)
        y_persist.append(temp[t])           # persistencia: amanha = hoje

    y_true = np.array(y_true)
    m_llm = regression_metrics(y_true, np.array(y_llm))
    m_base = regression_metrics(y_true, np.array(y_persist))
    print(f"== LLM previsor ({a.provider}) — últimos {len(y_true)} dias do teste ==")
    print(f"  persistência (baseline): mae={m_base['mae']:.3f}")
    print(f"  LLM ({a.provider})      : mae={m_llm['mae']:.3f}  -> "
          f"{'BATEU' if m_llm['mae'] < m_base['mae'] else 'não bateu'} a persistência")
    if a.provider == "echo":
        print("  [echo e stub offline = persistência; use openai/anthropic/nvidia p/ real]")


if __name__ == "__main__":
    main()
