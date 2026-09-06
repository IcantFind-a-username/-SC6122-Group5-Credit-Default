"""Shared artifact IO; preserve full probability precision and immutable run files."""
import hashlib
import json
import math
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def normalize(value: Any) -> Any:
    """Convert dataclasses/numpy scalars; reject nonfinite numbers, never round scores."""
    if is_dataclass(value) and not isinstance(value, type):
        value = asdict(value)
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, dict):
        return {str(k): normalize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [normalize(v) for v in value]
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("Nonfinite artifact value")
    return value


def write_json(path: Path, value: Any) -> None:
    """Write human-readable JSON atomically without changing historical files."""
    text = json.dumps(normalize(value), indent=2, allow_nan=False) + "\n"
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def bytes_hash(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def file_hash(path: Path) -> str:
    return bytes_hash(path.read_bytes())


def save_predictions(path, row_ids, labels, baseline, tuned):
    """Read this CSV with pandas float_precision='round_trip'."""
    pd.DataFrame({"row_id": np.asarray(row_ids), "default": np.asarray(labels),
                  "Baseline_probability": np.asarray(baseline, dtype=float),
                  "Tuned_probability": np.asarray(tuned, dtype=float)}).to_csv(path, index=False)
