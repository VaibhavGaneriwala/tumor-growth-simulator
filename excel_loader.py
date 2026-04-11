# Author: Mahera Sultana Shaik
# Description: reads, convert excel data into Patient objects

import pandas as pd
from src.core.visit_grouping import group_rows_into_patients

CLINICAL_SHEET_NAME = "Clinical_data"


def read_clinical_rows(filepath, sheet_name=CLINICAL_SHEET_NAME):
    """Read the clinical sheet from the Excel workbook and return rows as a list of dicts."""
    df = pd.read_excel(filepath, sheet_name=sheet_name)
    rows = df.to_dict("records")
    return rows

def load_patients_from_excel(filepath, sheet_name=CLINICAL_SHEET_NAME):
    """Read Excel file and group rows into Patient objects."""
    rows = read_clinical_rows(filepath, sheet_name=sheet_name)
    patients, summary = group_rows_into_patients(rows)
    return patients, summary