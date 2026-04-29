# Author: Vaibhav Ganeriwala
# Description: One-off script to build the training dataset for the growth-rate
#              predictor. Run this manually — not part of the Streamlit app.

import os
import sys
from src.core.excel_loader import load_patients_from_excel
from src.ml.dataset_builder import build_training_dataset

CLINICAL_EXCEL_PATH = os.environ.get("TGS_FILE_PATH", "")
NIFTI_ROOT = os.environ.get("TGS_NIFTI_ROOT", "")
OUTPUT_CSV = "models/training_data.csv"

MAX_PATIENTS = None

def main():
    if not CLINICAL_EXCEL_PATH or not os.path.exists(CLINICAL_EXCEL_PATH):
        sys.exit(
            "Error: clinical Excel file not found. Set the TGS_FILE_PATH "
            "environment variable to its location, e.g.\n"
            "  export TGS_FILE_PATH=/path/to/clinical_data.xlsx"
        )
    if not NIFTI_ROOT or not os.path.isdir(NIFTI_ROOT):
        sys.exit(
            "Error: NIfTI root folder not found. Set the TGS_NIFTI_ROOT "
            "environment variable to its location, e.g.\n"
            "  export TGS_NIFTI_ROOT=/path/to/nifti_root"
        )
    print(f"Loading patients from {CLINICAL_EXCEL_PATH}...")
    patients, summary = load_patients_from_excel(CLINICAL_EXCEL_PATH)
    print(f"Loaded {summary['total_patients']} patients with {summary['built_visits']} visits.\n")

    print(f"Building training dataset (max_patients={MAX_PATIENTS})...\n")
    result = build_training_dataset(
        patients=patients,
        nifti_root=NIFTI_ROOT,
        output_csv_path=OUTPUT_CSV,
        max_patients=MAX_PATIENTS,
        verbose=True,
    )

    print("\n--- Training rows ---")
    for row in result["training_rows"]:
        print(row)

    print("\n--- Skipped rows ---")
    for row in result["skipped_rows"]:
        print(row)

    print(f"\nSummary: {result['summary']}")


if __name__ == "__main__":
    main()