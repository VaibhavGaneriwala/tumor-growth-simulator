# Author: Karthik Mudenahalli Ashoka
# Description: Streamlit tab for viewing MRI volumes and running the tumor detection pipeline. 

import os
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from src.core.nifti_loader import (find_visit_sequences, load_nifti_volume, extract_slice, middle_slice_index, SEQUENCE_NAMES)
from src.core.image_processing import process_slice_pipeline

@st.cache_data(show_spinner="Loading MRI volume...")
def cached_load_volume(filepath):
    """Load a NIfTI volume and cache it for the session."""
    return load_nifti_volume(filepath)

@st.cache_data(show_spinner=False)
def cached_find_sequences(nifti_root, patient_id, study_datetime_str):
    """Cache the on-disk sequence lookup so we don't re-stat folders."""
    return find_visit_sequences(nifti_root, patient_id, study_datetime_str)

def _render_slice_image(slice_2d, voxel_dims_xy, title=""):
    """Build a matplotlib figure showing one slice with the correct aspect ratio"""
    dx, dy = voxel_dims_xy
    aspect_ratio = dy / dx if dx > 0 else 1.0

    fig, ax = plt.subplots(figsize=(6, 6))
    if slice_2d.ndim == 3:
        ax.imshow(slice_2d[:, :, ::-1], aspect=aspect_ratio)
    else:
        ax.imshow(slice_2d, cmap="gray", aspect=aspect_ratio)
    ax.set_title(title)
    ax.axis("off")
    return fig

def render(patients, nifti_root):
    """Render the MRI Viewer tab."""
    st.header("MRI Viewer")

    if patients is None or len(patients) == 0:
        st.warning("Load the clinical Excel file from the sidebar first.")
        return

    if not nifti_root:
        st.warning("Enter the NIfTI root folder path in the sidebar.")
        return

    if not os.path.exists(nifti_root):
        st.error(f"NIfTI root folder not found: `{nifti_root}`")
        return

    selected_id = st.session_state.get("selected_patient_id")
    selected_visit_idx = st.session_state.get("selected_visit_index", 0)
    if selected_id is None:
        st.info("Open the **Patient Explorer** tab and pick a patient + visit first.")
        return

    patient = None
    for p in patients:
        if p.patient_id == selected_id:
            patient = p
            break
    if patient is None:
        st.error(f"Patient '{selected_id}' not found.")
        return

    sorted_visits = patient.get_visits_sorted()
    if not sorted_visits:
        st.info("This patient has no imaging visits.")
        return
    if selected_visit_idx >= len(sorted_visits):
        selected_visit_idx = 0

    visit = sorted_visits[selected_visit_idx]
    study_datetime_str = visit.study_datetime.strftime("%Y-%m-%d_%H-%M-%S")

    st.caption(
        f"Patient **{patient.patient_id}** — Visit "
        f"{selected_visit_idx + 1}/{len(sorted_visits)} on "
        f"{visit.study_datetime.strftime('%Y-%m-%d %H:%M')}"
    )

    sequences = cached_find_sequences(nifti_root, patient.patient_id, study_datetime_str)
    available = [seq for seq in SEQUENCE_NAMES if sequences.get(seq) is not None]

    if not available:
        st.error(
            f"No NIfTI files found for this visit at "
            f"`{os.path.join(nifti_root, patient.patient_id, study_datetime_str.split('_')[0])}`"
        )
        return

    col1, col2, col3 = st.columns(3)
    with col1:
        chosen_seq = st.selectbox("MRI sequence", options=available, index=0, help="Only sequences that exist on disk for this visit are listed.")
    with col2:
        axis_label = st.radio("View axis", options=["Axial", "Sagittal", "Coronal"], index=0, horizontal=True)
    axis_map = {"Sagittal": 0, "Coronal": 1, "Axial": 2}
    axis = axis_map[axis_label]

    filepath = sequences[chosen_seq]
    try:
        volume_info = cached_load_volume(filepath)
    except Exception as exc:
        st.error(f"Failed to load NIfTI: {exc}")
        return

    volume_3d = volume_info["array"]
    voxel_dims = volume_info["voxel_dims"]
    max_index = volume_3d.shape[axis] - 1
    default_idx = middle_slice_index(volume_3d, axis)

    with col3:
        slice_index = st.slider(f"Slice index (0–{max_index})", min_value=0, max_value=max_index, value=default_idx, step=1)

    st.subheader("Detection pipeline")
    opt_col1, opt_col2, opt_col3, opt_col4 = st.columns(4)
    with opt_col1:
        apply_clahe = st.checkbox("CLAHE contrast", value=True)
    with opt_col2:
        run_detection = st.checkbox("Detect bright regions", value=True)
    with opt_col3:
        clean_mask = st.checkbox("Clean mask", value=True)
    with opt_col4:
        threshold_mode = st.radio("Threshold", options=["otsu", "manual"], index=0, horizontal=True)

    manual_threshold = 180
    if threshold_mode == "manual":
        manual_threshold = st.slider("Manual threshold (0-255)", min_value=0, max_value=255, value=180, step=1)

    slice_2d = extract_slice(volume_3d, axis=axis, index=slice_index)

    # Voxel dims
    dims_for_display = {
        0: (voxel_dims[1], voxel_dims[2]),  # sagittal: y,z
        1: (voxel_dims[0], voxel_dims[2]),  # coronal: x,z
        2: (voxel_dims[0], voxel_dims[1]),  # axial: x,y
    }[axis]

    if run_detection:
        result = process_slice_pipeline(slice_2d, threshold=manual_threshold, threshold_mode=threshold_mode, apply_clahe=apply_clahe, clean_mask=clean_mask, min_contour_area=20)
    else:
        result = None

    img_col1, img_col2 = st.columns(2)
    with img_col1:
        fig = _render_slice_image(slice_2d, dims_for_display, title=f"{chosen_seq} — raw")
        st.pyplot(fig, clear_figure=True)
        st.caption(
            f"Volume shape: {volume_info['shape']} • "
            f"Voxel size: {voxel_dims[0]:.1f}×{voxel_dims[1]:.1f}×{voxel_dims[2]:.1f} mm"
        )

    with img_col2:
        if result is not None:
            fig2 = _render_slice_image(
                result["overlay"], dims_for_display, title="Detected regions"
            )
            st.pyplot(fig2, clear_figure=True)
            st.caption(
                f"Regions found: **{result['num_regions']}** • "
                f"Threshold used: **{result['threshold_used']:.0f}** • "
                f"Mask pixels: {int(np.sum(result['mask'] > 0))}"
            )
        else:
            st.info("Enable 'Detect bright regions' to run the pipeline.")