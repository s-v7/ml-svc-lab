"""
    Metrics transversais (servem a qualquer experimento).
    Regressão: MAE, RMSE, MAPE.
    Classificação: acurácia, precisão, recall, F1, AUC.
"""
from __future__ import annotations

import numpy as np

def regression_metrics(y_true, y_pred) -> dict:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)

    err = y_pred - y_true
    mae = float(np.mean(np.abs(err)))
    rmse = float(np.sqrt(np.mean(err ** 2)))

    # MAPE robusto (ignora zeros no denominador)
    nz = y_true != 0
    mape = float(np.mean(np.abs(err[nz] / y_true[nz])) * 100) if nz.any() else float("nan")

    return {"mae": mae, "rmse": rmse, "mape": mape}

def classification_metrics(y_true, y_pred, y_prob=None) -> dict:
    from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score, roc_auc_score)

    y_true = np.asarray(y_true).astype(int)
    y_pred = np.asarray(y_pred).astype(int)

    out = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1":   float(f1_score(y_true, y_pred, zero_division=0))
    }

    if y_prob is not None and len(np.unique(y_true)) > 1:
        out["auc"] = float(roc_auc_score(y_true, np.asarray(y_prob, dtype=float)))
    return out

