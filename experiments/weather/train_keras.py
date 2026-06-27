"""
train_keras.py - FASE 2: redes neurais (TensorFlow/Keras) vs os baselines.

Arquiteturas crescentes, para os dois alvos, com tf.data e split TEMPORAL:
  - MLP     (denso sobre a janela achatada)
  - 1D-CNN  (padroes locais na janela)
  - LSTM    (sequencia explicita)

Regua (Fase 0/1, dado real de Teresina):
  - temperatura: persistencia MAE = 0.637  (LinearRegression chegou a 0.615)
  - chuva:       persistencia F1  = 0.759

Higiene: janelas em ordem temporal, scaler ajustado SO no treino, sem vazamento.

Uso: PYTHONPATH=. python3 -m experiments.weather.train_keras --janela 14 --epochs 40
"""
from __future__ import annotations
import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")  # silencia logs do TF

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import tensorflow as tf  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402

from common.data import load_table        # noqa: E402
from common.splits import temporal_split  # noqa: E402
from common.metrics import regression_metrics, classification_metrics  # noqa: E402
from experiments.weather.features import monta, FEATURES_BASE  # noqa: E402
from experiments.weather.windowing import make_windows  # noqa: E402

DADOS = "experiments/weather/data/weather_teresina.csv"
SEED = 42


def _ds(X, y, batch=32, shuffle=False):
    ds = tf.data.Dataset.from_tensor_slices((X.astype("float32"), y.astype("float32")))
    if shuffle:
        ds = ds.shuffle(2048, seed=SEED)
    return ds.batch(batch).prefetch(tf.data.AUTOTUNE)


def _build(arch: str, janela: int, n_feat: int, task: str):
    L = tf.keras.layers
    entrada = tf.keras.Input(shape=(janela, n_feat))
    if arch == "mlp":
        x = L.Flatten()(entrada)
        x = L.Dense(64, activation="relu")(x)
        x = L.Dropout(0.1)(x)
    elif arch == "cnn":
        x = L.Conv1D(32, 3, activation="relu", padding="same")(entrada)
        x = L.Conv1D(32, 3, activation="relu", padding="same")(x)
        x = L.GlobalAveragePooling1D()(x)
        x = L.Dense(32, activation="relu")(x)
    elif arch == "lstm":
        x = L.LSTM(32)(entrada)
        x = L.Dense(16, activation="relu")(x)
    else:
        raise ValueError(arch)

    if task == "reg":
        saida = L.Dense(1)(x)
        loss, metrics = "mse", ["mae"]
    else:
        saida = L.Dense(1, activation="sigmoid")(x)
        loss, metrics = "binary_crossentropy", ["AUC"]
    model = tf.keras.Model(entrada, saida)
    model.compile(optimizer="adam", loss=loss, metrics=metrics)
    return model


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--janela", type=int, default=14)
    ap.add_argument("--epochs", type=int, default=40)
    a = ap.parse_args()

    tf.keras.utils.set_random_seed(SEED)

    X, y_temp, y_rain = monta(load_table(DADOS))
    Xv = X.to_numpy(dtype=float)
    n_feat = Xv.shape[1]
    i_temp = FEATURES_BASE.index("temperature_2m_mean")
    i_prec = FEATURES_BASE.index("precipitation_sum")

    # janelas (ordem temporal preservada)
    Xw, yt = make_windows(Xv, y_temp.to_numpy(dtype=float), a.janela)
    _, yr = make_windows(Xv, y_rain.to_numpy().astype(int), a.janela)

    tr, va, te = temporal_split(len(Xw))

    # scaler por feature, ajustado SO no treino (reshape 3D->2D->3D)
    sc = StandardScaler().fit(Xw[tr].reshape(-1, n_feat))
    Xs = sc.transform(Xw.reshape(-1, n_feat)).reshape(Xw.shape)

    # baselines no MESMO teste (ultimo dia da janela = "hoje")
    hoje_temp = Xw[te, -1, i_temp]
    base_mae = regression_metrics(yt[te], hoje_temp)["mae"]
    choveu_hoje = (Xw[te, -1, i_prec] > 1.0).astype(int)
    base_f1 = classification_metrics(yr[te], choveu_hoje)["f1"]

    # padroniza o ALVO da regressao (fit so no treino); desnormaliza p/ medir
    ty_mean = float(yt[tr].mean())
    ty_std = float(yt[tr].std() or 1.0)
    yt_n = (yt - ty_mean) / ty_std

    cb = [tf.keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True)]

    print(f"== TEMPERATURA (regressao) — teste | baseline persistencia MAE={base_mae:.3f} ==")
    for arch in ["mlp", "cnn", "lstm"]:
        m = _build(arch, a.janela, n_feat, "reg")
        m.fit(_ds(Xs[tr], yt_n[tr], shuffle=True), validation_data=_ds(Xs[va], yt_n[va]),
              epochs=a.epochs, callbacks=cb, verbose=0)
        pred_n = m.predict(_ds(Xs[te], yt_n[te]), verbose=0).ravel()
        pred = pred_n * ty_std + ty_mean
        met = regression_metrics(yt[te], pred)
        flag = "BATEU" if met["mae"] < base_mae else "nao bateu"
        print(f"  {arch.upper():5s} mae={met['mae']:.3f} rmse={met['rmse']:.3f}  -> {flag}")

    print(f"== CHUVA (classificacao) — teste | baseline persistencia F1={base_f1:.3f} ==")
    for arch in ["mlp", "cnn", "lstm"]:
        m = _build(arch, a.janela, n_feat, "clf")
        m.fit(_ds(Xs[tr], yr[tr], shuffle=True), validation_data=_ds(Xs[va], yr[va]),
              epochs=a.epochs, callbacks=cb, verbose=0)
        prob = m.predict(_ds(Xs[te], yr[te]), verbose=0).ravel()
        pred = (prob > 0.5).astype(int)
        met = classification_metrics(yr[te], pred, prob)
        flag = "BATEU" if met["f1"] > base_f1 else "nao bateu"
        print(f"  {arch.upper():5s} f1={met['f1']:.3f} auc={met['auc']:.3f}  -> {flag}")


if __name__ == "__main__":
    main()
