from __future__ import annotations
from pathlib import Path
import pandas as pd

def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]

def read_csv(rel_path: str) -> pd.DataFrame:
    path = repo_root() / rel_path
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    return pd.read_csv(path)

def write_md(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
