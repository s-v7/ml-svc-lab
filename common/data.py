"""
    I/O de datasets (CSV e Parquet), transversal aos experimentos.
"""

from __future__ import annotations
from pathlib import Path
import pandas as pd

def save_table(df: pd.DataFrame, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".parquet":
        df.to_parquet(path, index=False)
    else:
        df.to_csv(path, index=False)
    return path

def load_table(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Não encontrei {path}")
    return pd.read_parquet(path) if path.suffix == ".parquet" else pd.read_csv(path)

