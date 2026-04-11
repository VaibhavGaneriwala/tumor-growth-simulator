# Author: Mahera Sultana Shaik
# Description: Unit tests for src/core/excel_loader.py

import pandas as pd
from src.core.excel_loader import read_clinical_rows, load_patients_from_excel

def _build_sample_excel(tmp_path):
    """Helper that writes a small fake Yale-style Excel file and returns its path."""
    df = pd.DataFrame([
        {
            "patient_id": "YG_FAKE001",
            "study_datetime": "2020-01-15_09-30-00",
            "age_at_Imaging (years)": 55,
            "sex": "Female",
        },
        {
            "patient_id": "YG_FAKE001",
            "study_datetime": "2020-07-15_09-30-00",
            "age_at_Imaging (years)": 56,
            "sex": "Female",
        },
        {
            "patient_id": "YG_FAKE002",
            "study_datetime": "2019-05-01_14-00-00",
            "age_at_Imaging (years)": 70,
            "sex": "Male",
        },
    ])
    filepath = tmp_path / "sample_clinical.xlsx"
    df.to_excel(filepath, sheet_name="Clinical_data", index=False)
    return filepath


def test_read_clinical_rows_returns_list_of_dicts(tmp_path):
    filepath = _build_sample_excel(tmp_path)
    rows = read_clinical_rows(filepath)
    assert isinstance(rows, list)
    assert len(rows) == 3
    assert isinstance(rows[0], dict)
    assert rows[0]["patient_id"] == "YG_FAKE001"


def test_load_patients_from_excel_end_to_end(tmp_path):
    filepath = _build_sample_excel(tmp_path)
    patients, summary = load_patients_from_excel(filepath)

    assert summary["total_rows"] == 3
    assert summary["built_visits"] == 3
    assert summary["skipped_rows"] == 0
    assert summary["total_patients"] == 2

    assert len(patients) == 2
    assert patients[0].patient_id == "YG_FAKE001"
    assert patients[0].num_visits() == 2
    assert patients[0].sex == "Female"
    assert patients[1].patient_id == "YG_FAKE002"
    assert patients[1].num_visits() == 1