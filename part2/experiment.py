"""Run from repository root: python -m part2.experiment

Reads the team's supplied splits. Uses the exact Part 4 development split,
CV folds, nominal-feature encoding, AP selection and score >= 0.5 rule.
No threshold optimization and no refit on validation observations.
"""
import argparse
import hashlib
import importlib.metadata
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import ParameterGrid, StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier, export_text

# Shared, already reviewed metrics and splitting. Does not import XGBoost.
from part4.evaluation import feature_target, metrics, split_development

ROOT = Path(__file__).resolve().parents[1]
GRID = {'max_depth': [2, 3, 4, 5, 6, 8, None], 'min_samples_leaf': [1, 20, 100]}


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_pipeline(params):
    prep = ColumnTransformer([
        ('categorical', OneHotEncoder(handle_unknown='ignore', sparse_output=False),
         ['SEX', 'EDUCATION', 'MARRIAGE'])], remainder='passthrough',
        verbose_feature_names_out=False)
    return Pipeline([('preprocess', prep), ('model', DecisionTreeClassifier(
        random_state=42, criterion='gini', class_weight=None, **params))])


def save_predictions(path, frame, baseline, tuned):
    x, y = feature_target(frame)
    pd.DataFrame({'row_id': frame.row_id.to_numpy(), 'default': y.to_numpy(),
                  'Baseline_probability': baseline.predict_proba(x)[:, 1],
                  'Tuned_probability': tuned.predict_proba(x)[:, 1]}).to_csv(path, index=False)


def save_rules(output, tuned, x_fit, y_fit):
    tree = tuned.named_steps['model']
    prep = tuned.named_steps['preprocess']
    names = prep.get_feature_names_out().tolist()
    transformed = prep.transform(x_fit)
    leaves = tree.apply(transformed)
    rules = []

    def walk(node, conditions):
        if tree.tree_.children_left[node] == -1:
            mask = leaves == node
            n = int(mask.sum())
            defaults = int(np.asarray(y_fit)[mask].sum())
            rules.append({'Leaf': int(node), 'Conditions': ' AND '.join(conditions),
                          'Fit_samples': n, 'Fit_defaults': defaults,
                          'Fit_default_rate': defaults / n,
                          'Predicted_default_at_0.5': int(defaults / n >= .5)})
            return
        name, value = names[tree.tree_.feature[node]], tree.tree_.threshold[node]
        walk(tree.tree_.children_left[node], conditions + [f'{name} <= {value:.8g}'])
        walk(tree.tree_.children_right[node], conditions + [f'{name} > {value:.8g}'])

    walk(0, [])
    pd.DataFrame(rules).sort_values('Fit_samples', ascending=False).to_csv(output / 'leaf_rules.csv', index=False)
    # Text export uses classifier argmax; at exactly 0.5 it differs from team >=.
    # Export paths with explicit team-rule labels instead of ambiguous class labels.
    text = '\n\n'.join(f"Leaf {r['Leaf']}: {r['Conditions']}\n"
                       f"Fit n={r['Fit_samples']}; default rate={r['Fit_default_rate']:.4f}; "
                       f"prediction (>=0.5)={r['Predicted_default_at_0.5']}" for r in rules)
    (output / 'tree_rules.txt').write_text(text + '\n', encoding='utf-8')
    return names


def run(output_dir=None):
    out = Path(output_dir).resolve() if output_dir else ROOT / 'results/decision_tree'
    if (out / 'protocol_frozen.json').exists():
        raise FileExistsError('Existing frozen run. Reproduce with --output-dir results/decision_tree_reproduction')
    out.mkdir(parents=True, exist_ok=True)
    train_path = ROOT / 'data/splits/train.csv'
    train = pd.read_csv(train_path)
    expected = pd.read_csv(ROOT / 'data/splits/train_indices.csv').row_id
    if len(train) != 24000 or len(train.columns) != 25 or train.row_id.tolist() != expected.tolist():
        raise ValueError('Training data do not match the team split.')
    fit, validation = split_development(train)
    x_fit, y_fit = feature_target(fit)
    x_val, y_val = feature_target(validation)
    assert len(fit) == 18000 and len(validation) == 6000
    assert set(fit.row_id).isdisjoint(validation.row_id)
    membership = pd.concat([fit[['row_id']].assign(Partition='fit'),
                            validation[['row_id']].assign(Partition='validation')], ignore_index=True)
    cv = list(StratifiedKFold(n_splits=5, shuffle=True, random_state=42).split(x_fit, y_fit))
    cv_members = pd.DataFrame([{'row_id': int(row), 'CV_fold': k}
                              for k, (_, holdout) in enumerate(cv) for row in fit.iloc[holdout].row_id])
    comparisons = {}
    for name, generated in [('development_membership.csv', membership), ('cv_membership.csv', cv_members)]:
        supplied = ROOT / 'results/xgboost' / name
        if supplied.exists():
            pd.testing.assert_frame_equal(generated.reset_index(drop=True), pd.read_csv(supplied))
            comparisons[name] = 'Exact membership and row order verified against Part 4'
        else:
            comparisons[name] = 'Generated using identical Part 4 splitting code; reference file absent'
        generated.to_csv(out / name, index=False)

    print('Part 2: 18,000 fit / 6,000 validation / 6,000 final test.', flush=True)
    settings = list(ParameterGrid(GRID))
    rows = []
    for number, params in enumerate(settings):
        scores = cross_validate(make_pipeline(params), x_fit, y_fit, cv=cv,
                                scoring={'AP': 'average_precision', 'ROC_AUC': 'roc_auc'},
                                return_train_score=True, n_jobs=2, error_score='raise')
        row = {'Candidate': number, 'Parameters': json.dumps(params),
               'Max_depth': 'Unlimited' if params['max_depth'] is None else params['max_depth'],
               'Min_samples_leaf': params['min_samples_leaf'],
               'Mean_CV_AP': float(scores['test_AP'].mean()),
               'SD_CV_AP': float(scores['test_AP'].std(ddof=1)),
               'Mean_fit_AP': float(scores['train_AP'].mean()),
               'Mean_CV_ROC_AUC': float(scores['test_ROC_AUC'].mean()),
               'SD_CV_ROC_AUC': float(scores['test_ROC_AUC'].std(ddof=1)),
               'Mean_fit_ROC_AUC': float(scores['train_ROC_AUC'].mean())}
        row.update({f'Fold_{k}_AP': float(v) for k, v in enumerate(scores['test_AP'])})
        rows.append(row)
        print(f"Candidate {number + 1}/21: {params}; CV AP={row['Mean_CV_AP']:.5f}", flush=True)
    results = pd.DataFrame(rows)
    results.to_csv(out / 'cv_results.csv', index=False)
    selected = int(results.sort_values(['Mean_CV_AP', 'Candidate'], ascending=[False, True]).iloc[0].Candidate)
    baseline_params = {'max_depth': None, 'min_samples_leaf': 1}
    baseline, tuned = make_pipeline(baseline_params), make_pipeline(settings[selected])
    baseline.fit(x_fit, y_fit)
    tuned.fit(x_fit, y_fit)
    for name, x, y in [('fit', x_fit, y_fit), ('validation', x_val, y_val)]:
        pd.DataFrame([{'Model': label, **metrics(y, model.predict_proba(x)[:, 1])}
                      for label, model in [('Baseline Decision Tree', baseline), ('Tuned Decision Tree', tuned)]]
                     ).to_csv(out / f'{name}_metrics.csv', index=False)
    save_predictions(out / 'validation_predictions.csv', validation, baseline, tuned)
    names = save_rules(out, tuned, x_fit, y_fit)
    for label, model in [('baseline', baseline), ('tuned', tuned)]:
        joblib.dump(model, out / f'{label}_pipeline.joblib', compress=3)
    protocol = {'Stage': 'Frozen before test loading', 'Frozen_at_UTC': datetime.now(timezone.utc).isoformat(),
                'Source_train_SHA256': file_hash(train_path),
                'Fit_rows': len(fit), 'Validation_rows': len(validation), 'CV_folds': 5, 'Seed': 42,
                'Features': x_fit.columns.tolist(), 'Transformed_features': names,
                'Search_space': GRID, 'Candidates': len(settings), 'Selection_metric': 'average_precision',
                'Tie_rule': 'Lowest candidate index', 'Selected_candidate': selected,
                'Selected_parameters': settings[selected], 'Baseline_parameters': baseline_params,
                'Prediction_rule': 'score >= 0.5', 'Threshold_tuned': False,
                'Refit_on_validation': False, 'Class_weight': None,
                'Part4_membership_checks': comparisons,
                'Source_repository': 'https://github.com/IcantFind-a-username/-SC6122-Group5-Credit-Default',
                'Source_commit': '0188f4a0df4e46140c8aa8ebfef4ba4a54403255',
                'Python': platform.python_version(),
                'Packages': {n: importlib.metadata.version(n) for n in ['numpy','pandas','scikit-learn','scipy','matplotlib','joblib']},
                'Model_SHA256': {n: file_hash(out / n) for n in ['baseline_pipeline.joblib','tuned_pipeline.joblib']}}
    write_json(out / 'protocol_frozen.json', protocol)
    print('Protocol and fitted models frozen. Evaluating final test data.', flush=True)
    test_path = ROOT / 'data/splits/test.csv'
    test = pd.read_csv(test_path)
    if len(test) != 6000 or test.columns.tolist() != train.columns.tolist():
        raise ValueError('Unexpected test schema/size')
    if test.row_id.tolist() != pd.read_csv(ROOT / 'data/splits/test_indices.csv').row_id.tolist():
        raise ValueError('Unexpected test order/membership')
    assert set(train.row_id).isdisjoint(test.row_id)
    x_test, y_test = feature_target(test)
    save_predictions(out / 'test_predictions.csv', test, baseline, tuned)
    final = pd.DataFrame([{'Model': label, **metrics(y_test, model.predict_proba(x_test)[:, 1])}
                          for label, model in [('Baseline Decision Tree', baseline), ('Tuned Decision Tree', tuned)]])
    final.to_csv(out / 'test_metrics.csv', index=False)
    fit_hash = pd.util.hash_pandas_object(train[x_test.columns], index=False)
    test_hash = pd.util.hash_pandas_object(x_test, index=False)
    write_json(out / 'data_audit.json', {'Source_test_SHA256':file_hash(test_path), 'Row_ID_overlap':0,
               'Training_rows':len(train), 'Test_rows':len(test),
               'Test_rows_with_features_seen_in_development':int(test_hash.isin(set(fit_hash)).sum()),
               'Note':'Identical feature vectors retained per team protocol; not proof of duplicate customers.'})
    write_json(out / 'run_metadata.json', {'Status':'Complete', 'Completed_at_UTC':datetime.now(timezone.utc).isoformat(),
               'Frozen_protocol_SHA256':file_hash(out / 'protocol_frozen.json'),
               'Test_predictions_SHA256':file_hash(out / 'test_predictions.csv')})
    print(final[['Model','AP','ROC-AUC','Accuracy','Precision','Recall','F1']].to_string(index=False))
    print('Selected parameters:', settings[selected])
    return out


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path)
    run(parser.parse_args().output_dir)
