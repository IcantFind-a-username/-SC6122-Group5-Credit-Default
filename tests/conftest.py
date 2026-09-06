import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def frame():
    def factory(n=80):
        return pd.DataFrame(
            {
                "row_id": np.arange(n),
                "SEX": [1, 2] * (n // 2),
                "EDUCATION": [1, 2, 3, 4] * (n // 4),
                "MARRIAGE": [1, 2] * (n // 2),
                "LIMIT_BAL": np.arange(n) * 1000,
                "default": [0, 0, 0, 1] * (n // 4),
            }
        )

    return factory


@pytest.fixture
def cases_frame():
    return pd.DataFrame(
        {
            "row_id": np.arange(8),
            "default": [1, 1, 1, 1, 0, 0, 0, 0],
            "Tuned_probability": [0.10, 0.20, 0.80, 0.90, 0.10, 0.25, 0.75, 0.85],
            "PAY_0": [-1, -1, 2, 2, -1, -1, 0, 0],
            "PAY_2": [-1, -1, 2, 2, -1, -1, 0, 0],
            "PAY_6": [-1, -1, 2, 2, -1, -1, 0, 0],
            "LIMIT_BAL": [10000] * 8,
            "BILL_AMT1": [500, 5000, 5000, 5000, 500, 5000, 5000, 5000],
            "PAY_AMT1": [500, 0, 500, 500, 500, 0, 500, 500],
            "BILL_AMT6": [500] * 8,
            "PAY_AMT6": [500] * 8,
            "AGE": [30] * 8,
            "SEX": [1, 2] * 4,
            "EDUCATION": [1, 2] * 4,
            "MARRIAGE": [1, 2] * 4,
        }
    )
