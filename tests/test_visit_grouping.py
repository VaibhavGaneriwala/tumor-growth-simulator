# Author: Vaibhav Ganeriwala
# Description: Unit tests for src/core/visit_grouping.py

from datetime import datetime

from src.core.visit_grouping import (parse_study_datetime, clean_age, clean_sex, build_visit_from_row, group_rows_into_patients)


def test_parse_study_datetime_valid():
    result = parse_study_datetime("2016-11-13_10-16-23")
    assert result == datetime(2016, 11, 13, 10, 16, 23)


def test_parse_study_datetime_bad_inputs():
    assert parse_study_datetime(None) is None
    assert parse_study_datetime("") is None
    assert parse_study_datetime("not a date") is None
    assert parse_study_datetime("2016-11-13") is None
    assert parse_study_datetime("nan") is None


def test_clean_age_valid_and_invalid():
    assert clean_age(71) == 71
    assert clean_age("45") == 45
    assert clean_age(-17) is None
    assert clean_age(150) is None
    assert clean_age(None) is None
    assert clean_age("not a number") is None


def test_clean_sex_normalization():
    assert clean_sex("Female") == "Female"
    assert clean_sex("male") == "Male"
    assert clean_sex("  MALE  ") == "Male"
    assert clean_sex("unknown") is None
    assert clean_sex(None) is None
    assert clean_sex("") is None


def test_build_visit_from_row_happy_path():
    row = {
        "patient_id": "YG_X",
        "study_datetime": "2020-05-01_12-00-00",
        "age_at_Imaging (years)": 60,
        "sex": "Female",
    }
    visit = build_visit_from_row(row)
    assert visit is not None
    assert visit.study_datetime == datetime(2020, 5, 1, 12, 0, 0)
    assert visit.age_at_study == 60


def test_build_visit_from_row_bad_date_returns_none():
    row = {"patient_id": "YG_X", "study_datetime": None, "age_at_Imaging (years)": 60}
    assert build_visit_from_row(row) is None


def test_group_rows_into_patients_basic():
    rows = [
        {
            "patient_id": "YG_A",
            "study_datetime": "2020-01-01_09-00-00",
            "age_at_Imaging (years)": 50,
            "sex": "Male",
        },
        {
            "patient_id": "YG_A",
            "study_datetime": "2020-06-01_09-00-00",
            "age_at_Imaging (years)": 50,
            "sex": "Male",
        },
        {
            "patient_id": "YG_B",
            "study_datetime": "2019-03-15_14-30-00",
            "age_at_Imaging (years)": 65,
            "sex": "Female",
        },
    ]
    patients, summary = group_rows_into_patients(rows)

    assert summary == {"total_rows": 3, "built_visits": 3, "skipped_rows": 0, "total_patients": 2}
    assert len(patients) == 2
    assert patients[0].patient_id == "YG_A"
    assert patients[0].num_visits() == 2
    assert patients[0].sex == "Male"
    assert patients[1].patient_id == "YG_B"
    assert patients[1].num_visits() == 1


def test_group_rows_skips_bad_rows():
    rows = [
        {"patient_id": "YG_A", "study_datetime": "2020-01-01_09-00-00", "age_at_Imaging (years)": 50},
        {"patient_id": None, "study_datetime": "2020-02-01_09-00-00", "age_at_Imaging (years)": 50},
        {"patient_id": "YG_B", "study_datetime": "garbage", "age_at_Imaging (years)": 60},
        {"patient_id": "YG_A", "study_datetime": "2020-03-01_09-00-00", "age_at_Imaging (years)": 50},
    ]
    patients, summary = group_rows_into_patients(rows)

    assert summary["total_rows"] == 4
    assert summary["built_visits"] == 2
    assert summary["skipped_rows"] == 2
    assert len(patients) == 1
    assert patients[0].patient_id == "YG_A"
    assert patients[0].num_visits() == 2