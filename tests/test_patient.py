# Author: Vaibhav Ganeriwala
# Description: Unit tests for the Patient class.

from datetime import datetime
from src.models.patient import Patient
from src.models.study_visit import StudyVisit

def test_empty_patient_has_no_visits():
    p = Patient(patient_id="YG_TEST001", sex="Female")
    assert p.num_visits() == 0
    assert p.first_visit_date() is None
    assert p.latest_visit_date() is None
    assert p.age_range() is None

def test_add_visit_and_sort_order():
    p = Patient(patient_id="YG_TEST002", sex="Male")
    v1 = StudyVisit(study_datetime=datetime(2018, 5, 1), age_at_study=60)
    v2 = StudyVisit(study_datetime=datetime(2017, 1, 15), age_at_study=59)
    v3 = StudyVisit(study_datetime=datetime(2019, 3, 10), age_at_study=61)
    p.add_visit(v1)
    p.add_visit(v2)
    p.add_visit(v3)
    assert p.num_visits() == 3
    sorted_visits = p.get_visits_sorted()
    assert sorted_visits[0].study_datetime == datetime(2017, 1, 15)
    assert sorted_visits[-1].study_datetime == datetime(2019, 3, 10)
    assert p.first_visit_date() == datetime(2017, 1, 15)
    assert p.latest_visit_date() == datetime(2019, 3, 10)
    assert p.age_range() == (59, 61)

def test_age_range_skips_missing_ages():
    p = Patient(patient_id="YG_TEST003")
    p.add_visit(StudyVisit(study_datetime=datetime(2020, 1, 1), age_at_study=None))
    p.add_visit(StudyVisit(study_datetime=datetime(2020, 6, 1), age_at_study=45))
    assert p.age_range() == (45, 45)
 
 
def test_lenient_validation_accepts_anything():
    p = Patient(patient_id="", sex="unknown")
    assert p.patient_id == ""
    assert p.sex == "unknown"
 
 
def test_study_visit_has_any_image():
    v_empty = StudyVisit(study_datetime=datetime(2020, 1, 1))
    assert v_empty.has_any_image() is False
 
    v_with_flair = StudyVisit(
        study_datetime=datetime(2020, 1, 1),
        flair_path="/data/scan_flair.nii.gz",
    )
    assert v_with_flair.has_any_image() is True