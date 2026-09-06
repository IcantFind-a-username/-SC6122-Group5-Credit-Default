"""Verify the committed cleaned data against a fresh official UCI download.

This is data-provenance verification only: no fitting or model selection.
"""
import json
from pathlib import Path
from urllib.request import urlopen

import pandas as pd
from ucimlrepo import fetch_ucirepo

from integration.artifacts import file_hash, write_json

ROOT = Path(__file__).resolve().parents[1]


def run():
    source = ROOT / 'data/source'
    source.mkdir(exist_ok=True)
    raw_path = source / 'uci_350_raw.csv'
    metadata_path = source / 'uci_metadata.json'
    if not raw_path.exists():
        dataset = fetch_ucirepo(id=350)
        url = dataset.metadata['data_url']
        with urlopen(url, timeout=60) as response:
            raw_path.write_bytes(response.read())
        write_json(metadata_path, dict(dataset.metadata))
    metadata = json.loads(metadata_path.read_text())
    raw = pd.read_csv(raw_path, float_precision='round_trip')
    expected = pd.read_csv(ROOT / 'data/credit_card_default_clean.csv', float_precision='round_trip')
    feature_names = expected.columns.drop(['row_id', 'default']).tolist()
    raw_features = raw[[f'X{i}' for i in range(1,24)]].copy()
    raw_features.columns = feature_names
    raw_features['default'] = raw['Y'].astype(int)
    duplicates_before = int(raw_features.duplicated().sum())
    cleaned = raw_features.copy()
    cleaned['EDUCATION'] = cleaned.EDUCATION.replace({0:4, 5:4, 6:4})
    cleaned['MARRIAGE'] = cleaned.MARRIAGE.replace({0:3})
    cleaned.insert(0, 'row_id', cleaned.index)
    pd.testing.assert_frame_equal(cleaned, expected, check_exact=True)
    report = {'source_url': metadata['data_url'], 'raw_sha256': file_hash(raw_path),
              'clean_sha256': file_hash(ROOT / 'data/credit_card_default_clean.csv'),
              'raw_columns': raw.columns.tolist(), 'raw_rows': len(raw),
              'raw_missing_values': int(raw.isna().sum().sum()),
              'original_id_matches_row_id_plus_one': bool((raw['ID'].to_numpy() == expected.row_id.to_numpy()+1).all()),
              'raw_duplicate_feature_label_rows_excluding_first': duplicates_before,
              'clean_duplicate_feature_label_rows_excluding_first': int(cleaned.drop(columns='row_id').duplicated().sum()),
              'cleaning_exact_values_dtypes_order_verified': True,
              'education_recoded_rows': int(raw_features.EDUCATION.isin([0,5,6]).sum()),
              'marriage_recoded_rows': int((raw_features.MARRIAGE==0).sum()),
              'clean_label_counts': expected.default.value_counts().sort_index().to_dict(),
              'source_license': 'CC BY 4.0; UCI dataset DOI 10.24432/C55S3H',
              'note': 'Fresh provenance audit; original preprocessing download bytes were not preserved. No training.'}
    write_json(ROOT / 'results/final/source_audit.json', report)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    run()
