![Python](https://img.shields.io/badge/Python-3.14-blue)
![Status](https://img.shields.io/badge/Project-Active-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

# Tumor Growth Simulator

A computational model that simulates tumor growth dynamics using medical imaging data and mathematical modeling.

Developed as part of final project for AA551: Engineering Python

## Overview
This project simulates the progression of tumor growth using imaging data and mathematical models to understand tumor expansion over time.

The simulator can help visualize tumor progression and analyze growth patterns.


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
• Logistic growth  
• Gompertz growth model  

This project explores simulation of tumor progression based on these models.

## 📊 Simulation Results


## ▶️ How to Run

Clone the repository
```bash 
git clone https://github.com/VaibhavGaneriwala/tumor-growth-simulator
cd tumor-growth-simulator
```

Install dependencies
```bash 
pip3 install -r requirements.txt
```

Run simulation
```bash 
python3 main.py
```

## 📜 License
MIT License

## 👨‍💻 Contributors
- Vaibhav Ganeriwala
- Mahera Sultana Shaik
- Karthik Mudenahalli Ashoka