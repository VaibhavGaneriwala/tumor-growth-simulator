# Author: Mahera Sultana Shaik
# Description: Loads MRI scans from dataset

import os
import nibabel as nib
import numpy as np

SEQUENCE_NAMES = ['PRE', 'POST', 'T2', 'FLAIR']

def build_nifti_path(root, patient_id, study_datetime_str, sequence):
    """Build path to NIFTI file and sequence directory."""
    date_only = study_datetime_str.split('_')[0]
    filename = f"{patient_id}_{study_datetime_str}_{sequence}.nii.gz"
    return os.path.join(root, patient_id, date_only, filename)

def find_visit_sequences(root, patient_id, study_datetime_str):
    """Find available sequences for a given visit."""
    sequences_found = {}
    for seq in SEQUENCE_NAMES:
        path = build_nifti_path(root, patient_id, study_datetime_str, seq)
        if os.path.exists(path):
            sequences_found[seq] = path
        else:
            sequences_found[seq] = None
    return sequences_found

def load_nifti_volume(filepath):
    """Load a NIFTI file and return the image data as a numpy array."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"NIfTI file not found: {filepath}")
    img = nib.load(filepath)
    array = np.asarray(img.get_fdata(), dtype=np.float32)
    zooms = img.header.get_zooms()
    voxel_dims = tuple(float(z) for z in zooms[:3])
    
    return {"array": array, "shape": tuple(array.shape), "voxel_dims": voxel_dims}

def extract_slice(volume_3d, axis, index):
    """Pull a single slice out of 3D MRI"""
    if axis not in (0, 1, 2):
        raise ValueError(f"axis must be 0, 1 or 2 (got {axis})")
    max_index = volume_3d.shape[axis] - 1
    if index < 0:
        index = 0
    elif index > max_index:
        index = max_index

    if axis == 0:
        slice_2d = volume_3d[index, :, :]
    elif axis == 1:
        slice_2d = volume_3d[:, index, :]
    else:
        slice_2d = volume_3d[:, :, index]
    return slice_2d

def middle_slice_index(volume_3d, axis):
    """helper function to return index of middle slice"""
    return volume_3d.shape[axis] // 2