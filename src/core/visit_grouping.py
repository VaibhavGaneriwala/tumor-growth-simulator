# Author: Vaibhav Ganeriwala
# Description: Helpers to group raw clinical-sheet rows into Patient objects

from datetime import datetime
from src.models.study_visit import StudyVisit
from src.models.patient import Patient

def parse_study_datetime(raw):
    """Parse raw datetime into datetime object"""
    if raw is None:
        return None
    text = str(raw).strip()
    if text == "" or text.lower() == "nan":
        return None
    parts = text.split("_")
    if len(parts) != 2:
        return None
    date_part, time_part = parts
    time_fixed = time_part.replace("-", ":")
    combined = f"{date_part} {time_fixed}"

    try:
        return datetime.strptime(combined, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None
    
def clean_age(raw):
    """Clean age_at_Imaging field"""
    if raw is None:
        return None
    try:
        if raw != raw:
            return None
    except TypeError:
        pass
    
    try:
        age = int(raw)
    except (ValueError, TypeError):
        return None
    if age < 0 or age > 120:
        return None
    return age

def clean_sex(raw):
    """Clean sex field in the dataset"""
    if raw is None:
        return None
    try:
        if raw != raw:
            return None
    except TypeError:
        pass
    text = str(raw).strip().title()
    if text in ("Male", "Female"):
        return text
    return None

def build_visit_from_row(row):
    """Convert single row into StudyVisit object"""
    when = parse_study_datetime(row.get("study_datetime"))
    if when is None:
        return None
    age = clean_age(row.get("age_at_Imaging (years)"))
    return StudyVisit(study_datetime=when, age_at_study=age)

def group_rows_into_patients(rows):
    """Group rows into Patient objects based on patient_id"""
    patients_by_id = {}
    total_rows = 0
    skipped_rows = 0
    built_visits = 0

    for row in rows:
        total_rows += 1
        raw_id = row.get("patient_id")
        if raw_id is None or str(raw_id).strip() == "":
            skipped_rows += 1
            continue
        patient_id = str(raw_id).strip()
        visit = build_visit_from_row(row)
        if visit is None:
            skipped_rows += 1
            continue
        if patient_id not in patients_by_id:
            patients_by_id[patient_id] = Patient(patient_id=patient_id, sex = clean_sex(row.get("sex")))
        patients_by_id[patient_id].add_visit(visit)
        built_visits += 1

    patients = sorted(patients_by_id.values(), key=lambda p: p.patient_id)
    summary = {
        "total_rows": total_rows,
        "built_visits": built_visits,
        "skipped_rows": skipped_rows,
        "total_patients": len(patients)
    }
    return patients, summary