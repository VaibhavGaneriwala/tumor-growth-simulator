# Author: Karthik Mudenahalli Ashoka
# Description: Streamlit tab showing a dataset-level overview as dashboard

import streamlit as st
from src.core.report import build_dataset_summary, build_patient_summary


def _find_patient_by_id(patients, patient_id):
    """Small helper — linear lookup, fine for 1,430-entry list."""
    for p in patients:
        if p.patient_id == patient_id:
            return p
    return None

def render(patients, nifti_root):
    """Render the Dashboard tab. Called by main.py with the loaded patient list."""
    st.header("Dashboard")

    if patients is None or len(patients) == 0:
        st.warning("No patients loaded yet. Enter the path to the clinical Excel file in the sidebar to begin.")
        return

    st.subheader("Dataset overview")

    total_patients = len(patients)
    total_visits = 0
    male_count = 0
    female_count = 0
    for p in patients:
        total_visits += p.num_visits()
        if p.sex == "Male":
            male_count += 1
        elif p.sex == "Female":
            female_count += 1
    avg_visits = total_visits / total_patients if total_patients > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Patients", total_patients)
    col2.metric("Total visits", total_visits)
    col3.metric("Avg visits / patient", f"{avg_visits:.1f}")
    col4.metric("Male / Female", f"{male_count} / {female_count}")

    with st.expander("Full dataset summary (text)", expanded=False):
        st.code(build_dataset_summary(patients), language="text")

    st.divider()

    st.subheader("Patient report")

    selected_id = st.session_state.get("selected_patient_id")
    if selected_id is None:
        st.info("No patient selected. Open the **Patient Explorer** tab and pick a patient to see their detailed report here.")
        return

    patient = _find_patient_by_id(patients, selected_id)
    if patient is None:
        st.error(f"Patient '{selected_id}' not found in the current dataset.")
        return
    tumor = st.session_state.get("tumor_for_selected_patient")
    if tumor is not None and tumor.patient_id != selected_id:
        tumor = None

    report_text = build_patient_summary(patient, tumor=tumor)
    st.code(report_text, language="text")

    if tumor is None:
        st.caption("💡 Open the MRI Viewer tab and run the detection pipeline on a few visits to populate tumor measurements. The growth rate and latest volume will then appear here.")