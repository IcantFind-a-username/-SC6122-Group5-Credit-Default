import pytest
from sklearn.model_selection import ParameterGrid

from part1.experiment import BASELINE, SEARCH_SPACE


@pytest.mark.parametrize("quantity,expected", [("candidates", 12), ("baseline_occurrences", 1)])
def test_declared_search_includes_unweighted_baseline(quantity, expected):
    settings = list(ParameterGrid(SEARCH_SPACE))
    observed = {"candidates": len(settings), "baseline_occurrences": settings.count(BASELINE)}
    assert observed[quantity] == expected
