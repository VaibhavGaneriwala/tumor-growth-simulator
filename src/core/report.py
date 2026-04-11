# Author: Mahera Sultana Shaik
# Description: Generates plain-text summary reports for patients.

def _format_date(dt):
    """Format a datetime as a short date string"""
    if dt is None:
        return "—"
    return dt.strftime("%Y-%m-%d")

def build_patient_summary(patient, tumor=None):
    """Build a multi-line text report summarizing one patient. If a Tumor object is supplied, its measurements and estimated growth rate are appended at the bottom."""
    lines = []
    lines.append(f"Patient ID: {patient.patient_id}")
    lines.append(f"Sex: {patient.sex if patient.sex else 'Unknown'}")
    lines.append(f"Number of imaging visits: {patient.num_visits()}")
 
    # Date range of the imaging timeline
    first = _format_date(patient.first_visit_date())
    last = _format_date(patient.latest_visit_date())
    lines.append(f"First visit: {first}")
    lines.append(f"Latest visit: {last}")
 
    # Age window across all visits (may be None if no ages known)
    age_window = patient.age_range()
    if age_window is None:
        lines.append("Age range: unknown")
    elif age_window[0] == age_window[1]:
        lines.append(f"Age at imaging: {age_window[0]}")
    else:
        lines.append(f"Age range: {age_window[0]}–{age_window[1]}")
 
    # tumor section
    if tumor is not None and tumor.num_measurements() > 0:
        lines.append("")
        lines.append("Tumor measurements:")
        lines.append(f"  Count: {tumor.num_measurements()}")
        lines.append(f"  Latest volume: {tumor.latest_volume():.1f} mm³")
 
        k = tumor.estimate_growth_rate()
        if k is None:
            lines.append("  Growth rate: not enough data")
        else:
            percent_per_month = (2.71828 ** (k * 30) - 1) * 100
            lines.append(
                f"  Growth rate k: {k:.5f} / day "
                f"(~{percent_per_month:+.1f}% per month)"
            )
 
    return "\n".join(lines)

def build_dataset_summary(patients):
    """
    Build a short overview report across an entire list of patients.
    """
    total = len(patients)
    if total == 0:
        return "No patients loaded."
 
    male_count = 0
    female_count = 0
    unknown_sex = 0
    total_visits = 0
    for p in patients:
        total_visits += p.num_visits()
        if p.sex == "Male":
            male_count += 1
        elif p.sex == "Female":
            female_count += 1
        else:
            unknown_sex += 1
 
    average_visits = total_visits / total if total > 0 else 0
 
    lines = [
        "Dataset summary",
        f"  Total patients: {total}",
        f"  Total imaging visits: {total_visits}",
        f"  Average visits per patient: {average_visits:.1f}",
        f"  Male: {male_count}",
        f"  Female: {female_count}",
        f"  Unknown sex: {unknown_sex}",
    ]
    return "\n".join(lines)