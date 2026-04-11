# Author: Karthik Mudenahalli Ashoka
# Description: Entry point for application

import os
import streamlit as st
from src.core.excel_loader import load_patients_from_excel


@st.cache_data(show_spinner="Loading patient data...")
def cached_load_patients(file_path):
    """Loads patient data from an Excel file with caching."""
    patients, summary = load_patients_from_excel(filepath=file_path)
    return patients, summary

def render_sidebar():
    """Renders the sidebar with file upload and summary display."""
    st.sidebar.header("Datatset")
    st.sidebar.caption("Point the app at the Yale Brain Mets Longitudinal files on your machine. These paths are used for this session only.")
    default_file_path = st.session_state.get("file_path", os.environ.get("TGS_FILE_PATH", ""))
    default_nifti_root = st.session_state.get("nifti_root", os.environ.get("TGS_NIFTI_ROOT", ""))
    file_path = st.sidebar.text_input("Clinical Excel file", value=default_file_path, help="Enter the path to the clinical Excel file.")
    nifti_root = st.sidebar.text_input("NIfTI root folder", value=default_nifti_root, help="Enter the path to the NIfTI root folder.")
    st.session_state["file_path"] = file_path
    st.session_state["nifti_root"] = nifti_root
    return file_path, nifti_root

def render_tab_safely(tab_name, import_path, function_name, **kwargs):
    """Renders a tab safely by importing the function dynamically."""
    try:
        module = __import__(import_path, fromlist=[function_name])
        render_fn = getattr(module, function_name)
    except (ImportError, AttributeError) as exc:
        st.info(f"**{tab_name}** is not implemented yet.")
        st.caption(f"(Missing `{import_path}.{function_name}`: {exc})")
        return
 
    render_fn(**kwargs)

def main():
    st.set_page_config(page_title="Tumor Growth Simulator", layout="wide")
    st.title("Tumor Growth Simulator")
    st.caption("Yale Brain Mets Longitudinal dataset explorer and tumor growth simulator")
    file_path, nifti_root = render_sidebar()

    patients = None
    summary = None
    if file_path and os.path.exists(file_path):
        try:
            patients, summary = cached_load_patients(file_path)
            st.sidebar.success(f"Loaded {summary['total_patients']} patients with {summary['built_visits']} visits.")
        except Exception as e:
            st.sidebar.error(f"Error loading patient data: {e}")
    elif file_path:
        st.sidebar.warning("File path not found.")
    else:
        st.sidebar.info("Please enter a valid file path to load patient data.")

    tab_explorer, tab_mri, tab_sim, tab_dashboard = st.tabs(['Patient Explorer', 'MRI Viewer', 'Tumor Growth Simulator', 'Dashboard'])
    tab_kwargs = {"patients": patients, "nifti_root": nifti_root}
    with tab_explorer:
        render_tab_safely("Patient Explorer", "src.gui.patient_tab", "render", **tab_kwargs)
    with tab_mri:
        render_tab_safely("MRI Viewer", "src.gui.mri_tab", "render", **tab_kwargs)
    with tab_sim:
        render_tab_safely("Tumor Growth Simulator", "src.gui.simulation_tab", "render", **tab_kwargs)
    with tab_dashboard:
        render_tab_safely("Dashboard", "src.gui.dashboard_tab", "render", **tab_kwargs)

if __name__ == "__main__":
    main()
