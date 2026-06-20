"""
    Modelos classicos (sklearn) vs os baselines.
    Salva plots (previsto x real, residuos, matriz de confusao) e imprime uma
    tabela de resultados em Markdown para colar no README.

    A regua (Fase 0, dado real de Teresina):
      - temperatura: persistencia MAE = 0.637 C
      - chuva:       persistencia F1  = 0.759
    Higiene anti-vazamento: split TEMPORAL, scaler ajustado SO no treino.

    Uso: PYTHONPATH=. python3 -m experiments.weather.train_sklearn
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402
from sklearn.linear_model import LinearRegression, Ridge, LogisticRegression  # noqa: E402
from sklearn.neural_network import MLPRegressor, MLPClassifier  # noqa: E402

from common.data import load_table        # noqa: E402
from common.splits import temporal_split  # noqa: E402
from common.metrics import regression_metrics, classification_metrics  # noqa: E402
from common.plots import plot_pred_vs_true, plot_residuals, plot_confusion  # noqa: E402
from experiments.weather.features import monta  # noqa: E402

DADOS = "experiments/weather/data/weather_teresina.csv"
PLOTS = "experiments/weather/plots"


def _fmt(d: dict) -> str:
    return "{" + ", ".join(f"{k}={v:.3f}" for k, v in d.items()) + "}"


def main(path: str = DADOS):
    X, y_temp, y_rain = monta(load_table(path))
    Xv = X.to_numpy(dtype=float)
    yt = y_temp.to_numpy(dtype=float)
    yr = y_rain.to_numpy().astype(int)

    tr, va, te = temporal_split(len(Xv))
    fit = np.concatenate([tr, va])
    scaler = StandardScaler().fit(Xv[fit])
    Xfit, Xte = scaler.transform(Xv[fit]), scaler.transform(Xv[te])

    hoje = X["temperature_2m_mean"].to_numpy(dtype=float)
    base_mae = regression_metrics(yt[te], hoje[te])["mae"]
    choveu_hoje = (X["precipitation_sum"].to_numpy() > 1.0).astype(int)
    base_f1 = classification_metrics(yr[te], choveu_hoje[te])["f1"]

    linhas_md = ["| Alvo | Modelo | Métrica | Bateu baseline? |",
                 "|------|--------|---------|:---:|",
                 f"| Temperatura | persistência (baseline) | MAE={base_mae:.3f} | — |"]

    print("== TEMPERATURA (regressão) — teste ==")
    print(f"  [baseline] persistência: mae={base_mae:.3f}")
    pred_para_plot = None
    for nome, modelo in [
        ("LinearRegression", LinearRegression()),
        ("Ridge(alpha=1)", Ridge(alpha=1.0)),
        ("MLPRegressor", MLPRegressor(hidden_layer_sizes=(32, 16), max_iter=800, random_state=0)),
    ]:
        modelo.fit(Xfit, yt[fit])
        pred = modelo.predict(Xte)
        m = regression_metrics(yt[te], pred)
        bateu = m["mae"] < base_mae
        print(f"  {nome:18s} {_fmt(m)}  -> {'BATEU' if bateu else 'nao bateu'}")
        linhas_md.append(f"| Temperatura | {nome} | MAE={m['mae']:.3f} | {'OK' if bateu else 'nao'} |")
        if nome == "LinearRegression":
            pred_para_plot = pred

    linhas_md.append(f"| Chuva | persistência (baseline) | F1={base_f1:.3f} | — |")
    print("== CHUVA (classificação) — teste ==")
    print(f"  [baseline] persistência: f1={base_f1:.3f}")
    pred_clf_plot = None
    for nome, modelo in [
        ("LogisticRegression", LogisticRegression(max_iter=1000)),
        ("MLPClassifier", MLPClassifier(hidden_layer_sizes=(32, 16), max_iter=800, random_state=0)),
    ]:
        modelo.fit(Xfit, yr[fit])
        prob = modelo.predict_proba(Xte)[:, 1]
        pred = modelo.predict(Xte)
        m = classification_metrics(yr[te], pred, prob)
        bateu = m["f1"] > base_f1
        print(f"  {nome:18s} {_fmt(m)}  -> {'BATEU' if bateu else 'nao bateu'}")
        linhas_md.append(f"| Chuva | {nome} | F1={m['f1']:.3f} (AUC={m['auc']:.3f}) | {'OK' if bateu else 'nao'} |")
        if nome == "MLPClassifier":
            pred_clf_plot = pred

    # plots (ultimos 120 dias do teste p/ legibilidade da serie)
    Path(PLOTS).mkdir(parents=True, exist_ok=True)
    jan = slice(-120, None)
    plot_pred_vs_true(yt[te][jan], pred_para_plot[jan],
                      f"{PLOTS}/temp_pred_vs_real.png",
                      "Temperatura: previsto (LinearRegression) vs real — ult. 120 dias")
    plot_residuals(yt[te], pred_para_plot, f"{PLOTS}/temp_residuos.png")
    plot_confusion(yr[te], pred_clf_plot, f"{PLOTS}/chuva_confusao.png")
    print(f"\nPlots salvos em {PLOTS}/")

    print("\n=== TABELA MARKDOWN (cole no README) ===")
    print("\n".join(linhas_md))


if __name__ == "__main__":
    main()
