"""
Controi features e os DOIS alvos e partir da serie diária crua.

Alvos (do DIA SEGUINTE, deslocados -1):
    - y_temp: temperature_2m_mean  de amanhã        (REGRESSÃO)
    - y_rain: chove amanhã!? precip_sum > limiar mm (CLASSIFICAÇÃO 0/1)

Features: variáveis do dia + sazonalidade (sin/cos do dia-do-ano)
"""
from __future__ import annotations

import numpy as np
import pandas as pd

LIMIAR_CHUVA_MM = 1.0 # >1mm/dia conta como "choveu"

FEATURES_BASE = [
    "temperature_2m_mean", "temperature_2m_max", "temperature_2m_min",
    "precipitation_sum", "wind_speed_10m_max", "shortwave_radiation_sum"
]

def monta(df: pd.DataFrame, limiar_chuva: float = LIMIAR_CHUVA_MM):
    """Retorna (X: DataFrame de features, y_temp: Series, y_rain: Series)."""
    df = df.copy()
    df["data"] = pd.to_datetime(df["data"])
    df = df.sort_values("data").reset_index(drop=True)

    # sazonalidade: dia do ano em seno/cosseno (captura o ciclo anual)
    doy = df["data"].dt.dayofyear.to_numpy()
    df["doy_sin"] = np.sin(2 * np.pi * doy / 365.25)
    df["doy_cos"] = np.cos(2 * np.pi * doy / 365.25)

    feats = FEATURES_BASE + ["doy_sin", "doy_cos"]
    # Alvos do dia seguinte
    y_temp = df["temperature_2m_mean"].shift(-1)
    y_rain = (df["precipitation_sum"].shift(-1) > limiar_chuva).astype("float")

    # Remove a última linha (sem alvo) e qualquer Nan das features
    X = df[feats]
    mask = y_temp.notna()
    X, y_temp, y_rain = X[mask], y_temp[mask], y_rain[mask]
    X = X.reset_index(drop=True)

    return X, y_temp.reset_index(drop=True), y_rain.reset_index(drop=True).astype(int)

