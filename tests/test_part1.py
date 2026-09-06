import numpy as np
import pytest
from sklearn.model_selection import ParameterGrid

from part1.experiment import BASELINE, SEARCH_SPACE, make_pipeline, run
from part4.evaluation import feature_target


@pytest.mark.parametrize("column,value", [("EDUCATION", 99), ("LIMIT_BAL", 1e12)])
def test_preprocessing_does_not_learn_prediction_values(frame, column, value):
    x, y = feature_target(frame())
    model = make_pipeline().fit(x, y)
    preprocess = model.named_steps["preprocess"]
    categories = [v.copy() for v in preprocess.named_transformers_["categorical"].categories_]
    means = preprocess.named_transformers_["remainder"].mean_.copy()
    unseen = x.iloc[:2].copy()
    unseen[column] = value
    assert np.isfinite(model.predict_proba(unseen)).all()
    assert np.array_equal(means, preprocess.named_transformers_["remainder"].mean_)
    assert all(np.array_equal(a, b) for a, b in zip(
        categories, preprocess.named_transformers_["categorical"].categories_))


def test_declared_search_includes_unweighted_baseline():
    settings = list(ParameterGrid(SEARCH_SPACE))
    assert len(settings) == 12
    assert settings.count(BASELINE) == 1


def test_frozen_supplement_cannot_be_overwritten(tmp_path):
    frozen = tmp_path / "protocol_frozen.json"
    frozen.write_text("frozen")
    with pytest.raises(FileExistsError, match="frozen"):
        run(tmp_path)
    assert frozen.read_text() == "frozen"
