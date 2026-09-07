"""Read frozen RF interpretation artifacts for both report and slides; no fitting."""
from pathlib import Path

from integration.audit import read_csv

ROOT = Path(__file__).resolve().parents[1]


def rf_interpretation():
    """Return saved importance and one pre-existing extreme example of each error."""
    folder = ROOT / 'results/rf'
    importance = read_csv(folder / 'validation_importance.csv')
    cases = read_csv(folder / 'misclassification_cases_05.csv')
    predictions = read_csv(folder / 'test_predictions.csv').set_index('row_id')
    examples = cases.groupby('Group', sort=False).head(1).set_index('Group')
    assert set(examples.index) == {'FN', 'FP'}
    for group, example in examples.iterrows():
        prediction = predictions.loc[example.row_id]
        assert example['default'] == prediction['default']
        assert example.Tuned_probability == prediction.Tuned_probability
        assert (group == 'FN' and example['default'] == 1 and example.Tuned_probability < .5) or (
            group == 'FP' and example['default'] == 0 and example.Tuned_probability >= .5)
    return importance, examples
