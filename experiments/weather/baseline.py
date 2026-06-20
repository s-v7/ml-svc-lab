"""
 Baselines do experimento weather.
 A regra que todo modelo de ML precisa BATER para "valer a pena".

 Temperatura (regressão):
    - persistência: amanhã = hoje
    - naive sazonal: amanhã = mesma dat a há 365 dias
 Chuva (classificação):
    - persitência: choveu hoje -> chove amanhã
    - climatologia: sempre preve a classe majoritára (taxa base)

 Use: python3 -m experiments.weather.baseline
 """
from __future__ import annotations
import sys
from pathlib import Path

# Permite rodar como script direto (adiciona a raiz do repo ao path)
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
from common.data import load_table
from common.splits import temporal_split
from common.metrics import regression_metrics, classification_metrics
from experiments.weather.features import monta

DADOS = "experiments/weather/data/weather_teresina.csv"

def avalia(path: str = DADOS):
    df = load_table(path)

    X, y_temp, y_rain = monta(df)
    n = len(X)
    _, _, te = temporal_split(n) # avalia no conjunto de teste (futuro)
    
    temp = y_temp.to_numpy()
    rain = y_rain.to_numpy()

    # ---TEMPERATURA (regressão) ----
    # persistência: previsão p/ y_temp[t] (= temp de amanhã) e a temp de hoje,
    # que e o prório temperature_2m_mean atual = X["temperature_2m_mean"][t]
    hoje = X["temperature_2m_mean"].to_numpy()
    pred_persist = hoje

    # naive sazonal: tem de 365 dias atrás (quando houver)
    pred_sazonal = np.concatenate([temp[:365], temp[:-365]]) if n > 365 else hoje

    print("=== TEMPERATURA (regressão) --- Conjunto de teste ===")
    print(" persistência :", _fmt(regression_metrics(temp[te], pred_persist[te])))
    print(" naive sazonal:", _fmt(regression_metrics(temp[te], pred_sazonal[te])))

    # --- CHUVA (classificação) ---
    choveu_hoje = (X["precipitation_sum"].to_numpy() > 1.0).astype(int)
    pred_persist_rain = choveu_hoje # choveu hoje -> chove amanhã
    base = int(round(rain[:n - len(te)].mean())) # classe majoritária no treino
    pred_clim = np.full_like(rain, base)

    print("=== CHUVA (classificação) --- conjunto de teste ===")
    print(f"   taxa base de chuva (treino): {rain[:n - len(te)].mean():.3f}")
    print("    persistência :", _fmt(classification_metrics(rain[te], pred_persist_rain[te])))
    print("    climatologia :", _fmt(classification_metrics(rain[te], pred_clim[te])))

def _fmt(d: dict) -> str:
    return "{" + ", ".join(f"{k}={v:.3f}" for k, v in d.items()) + "}"

if __name__ == "__main__":
    avalia()
