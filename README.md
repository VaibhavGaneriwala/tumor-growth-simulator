![Python](https://img.shields.io/badge/Python-3-blue)
![Status](https://img.shields.io/badge/Project-Active-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

# Tumor Growth Simulator

A web-based tool for exploring longitudinal brain MRI data and simulating tumor growth under different scenarios. Built with Streamlit on top of the Yale Brain Mets Longitudinal dataset.

Developed as part of final project for AA551: Engineering Python

## What it does

The Tumor Growth Simulator lets a user:
1. **Browse patients** from the Yale clinical dataset (~1,430 patients,
   ~11,884 imaging visits) and view each patient's longitudinal timeline.
2. **Scroll through MRI slices** (axial, sagittal, coronal) of any visit
   with optional CLAHE contrast enhancement and automatic tumor region
   highlighting via Otsu thresholding + contour detection.
3. **Simulate tumor growth** using three mathematical models (exponential,
   linear, Gompertz) with interactive sliders for starting volume and
   growth rate. An optional **ML-predicted growth rate** populates the
   slider with a value estimated by a Random Forest trained on the cohort.
4. **Run what-if scenarios** — compare a baseline trajectory against a
   hypothetical treatment that starts on a chosen day and changes the
   growth rate from that day forward.
5. **View a dashboard** summary of the entire dataset and detailed reports
   for individual patients.
6. **Export simulation results** as a CSV file for offline analysis.


## Dataset
This project uses the Brain Tumor MRI Dataset from Cancer Imaging Archive.

Dataset Link:
https://www.cancerimagingarchive.net/collection/yale-brain-mets-longitudinal

Dataset contains:
- Glioma
- Meningioma
- Pituitary tumors
- Healthy brain scans

## Project Goals
- Simulate tumor growth over time
- Analyze tumor progression from MRI data
- Visualize tumor expansion
- Study mathematical tumor growth models

## Project Architecture
```
Dataset (MRI Images)
        │
        ▼
Image Processing
        │
        ▼
Tumor Segmentation
        │
        ▼
Growth Modeling
        │
        ▼
Simulation Engine
        │
        ▼
Visualization
```

## Tumor Growth Modeling

Tumor growth often follows mathematical models such as:

• Exponential growth  
• Linear growth  
• Gompertz growth model  

This project explores simulation of tumor progression based on these models.

## Simulation Results


## How to Run

Clone the repository
```bash 
git clone https://github.com/VaibhavGaneriwala/tumor-growth-simulator
cd tumor-growth-simulator
```

Install dependencies
```bash 
pip3 install -r requirements.txt
```
Download the Yale Brain Mets Longitudinal dataset and note the path
   to its root folder (the one containing the `YG_*` patient subfolders).

Export PATHS
The dataset builder reads the same TGS_FILE_PATH and TGS_NIFTI_ROOT
environment variables used by the Streamlit app. Set them before running:

```bash
export TGS_FILE_PATH=/path/to/clinical_data.xlsx
export TGS_NIFTI_ROOT=/path/to/nifti_root
python run_dataset_build.py
python train_growth_model.py
```

Run simulation
```bash 
streamlit run main.py
```
Streamlit will open a browser tab at `http://localhost:8501`.

## License
MIT License

## Contributors
- Vaibhav Ganeriwala
- Mahera Sultana Shaik
- Karthik Mudenahalli Ashoka