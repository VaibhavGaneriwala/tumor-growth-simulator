# Author: Mahera Sultana Shaik
# Description: Unit tests for src/core/report.py

from datetime import datetime
from src.core.report import build_patient_summary, build_dataset_summary
from src.models.patient import Patient
from src.models.study_visit import StudyVisit
from src.models.tumor import Tumor


def _make_patient_with_visits():
    p = Patient(patient_id="YG_REPORT001", sex="Female")
    p.add_visit(StudyVisit(study_datetime=datetime(2020, 1, 15), age_at_study=55))
    p.add_visit(StudyVisit(study_datetime=datetime(2020, 7, 15), age_at_study=56))
    return p


def test_summary_includes_basic_fields():
    p = _make_patient_with_visits()
    text = build_patient_summary(p)
    assert "YG_REPORT001" in text
    assert "Female" in text
    assert "Number of imaging visits: 2" in text
    assert "2020-01-15" in text
    assert "2020-07-15" in text
    assert "Age range: 55–56" in text


def test_summary_handles_empty_patient():
    p = Patient(patient_id="YG_EMPTY")
    text = build_patient_summary(p)
    assert "YG_EMPTY" in text
    assert "Unknown" in text  # sex
    assert "Number of imaging visits: 0" in text
    assert "—" in text  # date placeholder
    assert "Age range: unknown" in text


def test_summary_with_tumor_shows_growth_rate():
    p = _make_patient_with_visits()
    t = Tumor(patient_id="YG_REPORT001")
    t.add_measurement(datetime(2020, 1, 15), 1000.0)
    t.add_measurement(datetime(2020, 7, 15), 2000.0)

    text = build_patient_summary(p, tumor=t)
    assert "Tumor measurements:" in text
    assert "Count: 2" in text
    assert "Latest volume: 2000.0 mm³" in text
    assert "Growth rate k:" in text
    assert "per month" in text


def test_summary_with_tumor_no_growth_rate_when_single_point():
    p = _make_patient_with_visits()
    t = Tumor(patient_id="YG_REPORT001")
    t.add_measurement(datetime(2020, 1, 15), 1000.0)
    text = build_patient_summary(p, tumor=t)
    assert "not enough data" in text


def test_dataset_summary_counts_correctly():
    patients = [
        Patient(patient_id="A", sex="Male"),
        Patient(patient_id="B", sex="Female"),
        Patient(patient_id="C", sex="Female"),
        Patient(patient_id="D", sex=None),
    ]
    patients[0].add_visit(StudyVisit(study_datetime=datetime(2020, 1, 1)))
    patients[0].add_visit(StudyVisit(study_datetime=datetime(2020, 6, 1)))
    patients[1].add_visit(StudyVisit(study_datetime=datetime(2019, 3, 1)))

    text = build_dataset_summary(patients)
    assert "Total patients: 4" in text
    assert "Total imaging visits: 3" in text
    assert "Male: 1" in text
    assert "Female: 2" in text
    assert "Unknown sex: 1" in text


def test_dataset_summary_empty_list():
    assert build_dataset_summary([]) == "No patients loaded."