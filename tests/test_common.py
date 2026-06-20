import numpy as np

from common.metrics import regression_metrics, classification_metrics
from common.splits import temporal_split, random_split
from experiments.weather.windowing import make_windows, flatten

def test_regression_metrics_perfeito():
    m = regression_metrics([1, 2, 3], [1, 2, 3])
    assert m["mae"] == 0 and m["rmse"] == 0

def test_classification_metrics_perfeito():
    m = classification_metrics([0, 1, 1], [0, 1, 1], y_prob=[0.1, 0.9, 0.8])
    assert m["accuracy"] == 1.0 and m["auc"] == 1.0

def test_temporal_split_ordem_e_tamanho():
    tr, va, te = temporal_split(100, 0.15, 0.15)
    assert len(tr) == 70 and len(va) == 15 and len(te) == 15
    assert tr.max() < va.min() < te.min()

def test_random_split_cobre_tudo():
    tr, va, te = random_split(100)
    assert len(set(tr) | set(va) | set(te)) == 100

def test_make_windows_shapes():
    X = np.arange(20 * 3).reshape(20, 3)
    y = np.arange(20)
    Xw, yw = make_windows(X, y, 5)
    assert Xw.shape == (15, 5, 3) and yw.shape == (15,)
    assert flatten(Xw).shape == (15, 15)

