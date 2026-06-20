"""
    Divisão de dados em treino/validação/teste;

    temporal_split: SEM embaralhar (obrigatório para series temporais; 
    embaralhar vaza o futuro no treino e infla as métricas)

    random_split: embaralhado(para experimentos i.i.d: classificação de imagem,
    text, tabular sem ordem temporal
"""
from __future__ import annotations

import numpy as np

def temporal_split(n: int, val_frac: float = 0.15, test_frac: float = 0.15):
    """Return (idx_treino, idx_val, idx_teste) preservando a ordem temporal."""
    assert 0 < val_frac + test_frac < 1, "frações inválida"

    n_test = int(round(n * test_frac))
    n_val = int(round(n * val_frac))
    n_train = n - n_val - n_test

    idx = np.arange(n)

    return idx[:n_train], idx[n_train:n_train + n_val], idx[n_train + n_val:]

def random_split(n: int, val_frac: float = 0.15, test_frac: float = 0.15, seed: int = 42):
    """Split embaralhar para dados sem dependência temporal."""
    
    rng = np.random.default_rng(seed)

    idx = rng.permutation(n)

    n_test = int(round(n * test_frac))
    n_val = int(round(n * val_frac))
    n_train = n - n_val - n_test
    
    return (idx[: n - n_val - n_test], idx[n - n_val - n_test: n - n_test], idx[n - n_test:])

