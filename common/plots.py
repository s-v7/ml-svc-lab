"""
    Plots de avaliação transversais (salvam em arquivo)
    Usa backend não-interativo (Agg) para rodar headless/CI.
"""
from __future__ import annotations
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt # noqa: E402 (após matplotlib.use)
import numpy as np

def _prep(path):
    path = Path(path)

    path.parent.mkdir(parents=True, exist_ok=True)

    return path

def plot_pred_vs_true(y_true, y_pred, path, titulo="Previsto vs Real"):
    path = _prep(path)

    fig, ax = plt.subplots(figsize=(10, 4))

    ax.plot(np.asarray(y_true), label="real", linewidth=1)
    ax.plot(np.asarray(y_pred), label="previsto", linewidth=2, alpha=0.8)
    ax.set_title(titulo)
    ax.legend()

    fig.tight_layout()
    fig.savefig(path, dpi=110)

    plt.close(fig)

    return path

def plot_residuals(y_true, y_pred, path, titulo="Residuos"):
    path = _prep(path)

    res = np.asarray(y_pred, dtype=float) - np.asarray(y_true, dtype=float)

    fig, ax = plt.subplots(figsize=(10, 3))

    ax.axhline(0, color="k", linewidth=0.8)
    ax.plot(res, linewidth=1)
    ax.set_title(f"{titulo} (média={res.mean():.3f})")

    fig.tight_layout()
    fig.savefig(path, dpi=110)

    plt.close(fig)

    return path

def plot_confusion(y_true, y_pred, path, labels=("nao", "sim")):
    from sklearn.metrics import confusion_matrix
    path = _prep(path)

    cm = confusion_matrix(np.asarray(y_true).astype(int), np.asarray(y_pred).astype(int))

    fig, ax = plt.subplots(figsize=(4, 4))

    im = ax.imshow(cm, cmap="Blues")
    for (i, j), v in np.ndenumerate(cm):
        ax.text(j, i, str(v), ha="center", va="center")

    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))

    ax.set_xticklabels(labels)
    ax.set_yticklabels(labels)

    ax.set_xlabel("previsto")
    ax.set_ylabel("real")

    fig.colorbar(im)
    fig.tight_layout()
    fig.savefig(path, dpi=110)

    plt.close(fig)

    return path

