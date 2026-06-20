"""
    - Janelas deslizantes para models de sequência (específicos de séries temporais)
    Retorna arrays numpy que servem tanto ao sklearn (achatado) quanto ao Keras/tf.data
    depois (formato 3D[amostras, tempo, features]).
"""
from __future__ import annotations
import numpy as np

def make_windows(X2d, y, input_width: int):
    """
    X2d: array [T, n_features] (uma linha por dia, já em ordem temporal)
    y: array [T] alinhado a X2d (alvo do dia seguinte ao último da janela)
    input_width: quantos dias passados entram em cada janela

    Retorna (Xw. yw):
        Xw: [N, inputs_width, n_features]
        yw: [N]
    onde N = T - input_width, e a janela[i .. (i+input_width)-1] preve y[(i+input_width)-1]
    """
    X2d = np.asarray(X2d, dtype=float)
    y = np.asarray(y)
    T = X2d.shape[0]
    if T <= input_width:
        raise ValueError(f"Série curta demais (T={T}) para janela {input_width}")
    Xw = np.stack([X2d[i:i + input_width] for i in range(T - input_width)])
    yw = y[input_width:]    # alvo do dia seguinte ao fim de cada janela
    return Xw, yw

def flatten(Xw):
    """[N, W, F] -> [N, W*F] para modelos que esperam vetor (ex: sklearn)."""
    Xw = np.asarray(Xw)
    return Xw.reshape(Xw.shape[0], -1)


