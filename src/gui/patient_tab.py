# Author: Karthik Mudenahalli Ashoka
# Description: Streamlit tab for browsing patients in the Yale dataset.

import streamlit as st


def render(patients, nifti_root):
    """Render the Patient Explorer tab. Called by main.py"""
    st.header("Patient Explorer")

    if patients is None or len(patients) == 0:
        st.warning("No patients loaded yet. Enter the path to the clinical Excel file in the sidebar to begin.")
        return

    st.caption(f"{len(patients)} patients available.")

    patient_ids = [p.patient_id for p in patients]
    previous_id = st.session_state.get("selected_patient_id")
    if previous_id in patient_ids:
        default_index = patient_ids.index(previous_id)
    else:
        default_index = 0

    selected_id = st.selectbox("Select a patient", options=patient_ids, index=default_index,help="Start typing a patient ID to filter the list.")

    st.session_state["selected_patient_id"] = selected_id

    selected_patient = None
    for p in patients:
        if p.patient_id == selected_id:
            selected_patient = p
            break

    if selected_patient is None:
        st.error("Selected patient not found. This should not happen.")
        return

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Patient ID", selected_patient.patient_id)
    col2.metric("Sex", selected_patient.sex if selected_patient.sex else "Unknown")
    col3.metric("Imaging visits", selected_patient.num_visits())

    age_window = selected_patient.age_range()
    if age_window is None:
        age_display = "—"
    elif age_window[0] == age_window[1]:
        age_display = f"{age_window[0]}"
    else:
        age_display = f"{age_window[0]}–{age_window[1]}"
    col4.metric("Age at imaging", age_display)

    st.subheader("Imaging visits")

    sorted_visits = selected_patient.get_visits_sorted()
    if not sorted_visits:
        st.info("This patient has no imaging visits recorded.")
        return

    visit_rows = []
    for i, v in enumerate(sorted_visits, start=1):
        visit_rows.append({
            "#": i,
            "Date & time": v.study_datetime.strftime("%Y-%m-%d %H:%M"),
            "Age": v.age_at_study if v.age_at_study is not None else "—",
        })

    st.dataframe(visit_rows, use_container_width=True, hide_index=True)

    st.subheader("Select a visit for the MRI Viewer")
    visit_labels = [
        f"{i + 1}. {v.study_datetime.strftime('%Y-%m-%d %H:%M:%S')}"
        for i, v in enumerate(sorted_visits)
    ]

    previous_visit_idx = st.session_state.get("selected_visit_index", 0)
    if previous_visit_idx >= len(sorted_visits):
        previous_visit_idx = 0

    selected_label = st.radio(
        "Visit", options=visit_labels, index=previous_visit_idx, label_visibility="collapsed")
    selected_visit_index = visit_labels.index(selected_label)
    st.session_state["selected_visit_index"] = selected_visit_index

    st.success(
        f"Selected visit {selected_visit_index + 1} of {len(sorted_visits)} "
        f"for {selected_patient.patient_id}. "
        f"Open the MRI Viewer tab to see the scans."
    )