# Author: Mahera Sultana Shaik
# Description: Unit tests for src/core/nifti_loader.py

import os
import nibabel as nib
import numpy as np
import pytest

from src.core.nifti_loader import (build_nifti_path, find_visit_sequences, load_nifti_volume, extract_slice, middle_slice_index, SEQUENCE_NAMES,)


def _make_fake_nifti(filepath, shape=(8, 10, 12), voxel_dims=(1.0, 1.0, 2.0)):
    """Helper that writes a tiny synthetic NIfTI file at the given path."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    array = np.arange(np.prod(shape), dtype=np.float32).reshape(shape)
    affine = np.diag([voxel_dims[0], voxel_dims[1], voxel_dims[2], 1.0])
    img = nib.Nifti1Image(array, affine)
    nib.save(img, filepath)


def test_build_nifti_path_uses_yale_layout():
    path = build_nifti_path(
        root="/data/raw",
        patient_id="YG_0B4NV6E3KEZQ",
        study_datetime_str="2015-09-29_12-36-27",
        sequence="FLAIR",
    )
    expected = (
        "/data/raw/YG_0B4NV6E3KEZQ/2015-09-29/"
        "YG_0B4NV6E3KEZQ_2015-09-29_12-36-27_FLAIR.nii.gz"
    )
    assert path == expected


def test_find_visit_sequences_partial(tmp_path):
    patient_id = "YG_FAKE001"
    study_datetime = "2020-01-15_09-30-00"
    date_only = "2020-01-15"
    visit_folder = tmp_path / patient_id / date_only

    flair_path = visit_folder / f"{patient_id}_{study_datetime}_FLAIR.nii.gz"
    post_path = visit_folder / f"{patient_id}_{study_datetime}_POST.nii.gz"
    _make_fake_nifti(str(flair_path))
    _make_fake_nifti(str(post_path))

    sequences = find_visit_sequences(str(tmp_path), patient_id, study_datetime)
    assert set(sequences.keys()) == set(SEQUENCE_NAMES)
    assert sequences["FLAIR"] is not None
    assert sequences["POST"] is not None
    assert sequences["PRE"] is None
    assert sequences["T2"] is None


def test_load_nifti_volume_returns_expected_shape(tmp_path):
    filepath = tmp_path / "tiny.nii.gz"
    _make_fake_nifti(str(filepath), shape=(8, 10, 12), voxel_dims=(1.0, 2.0, 3.0))

    volume = load_nifti_volume(str(filepath))
    assert volume["shape"] == (8, 10, 12)
    assert volume["array"].shape == (8, 10, 12)
    assert volume["voxel_dims"] == (1.0, 2.0, 3.0)
    assert volume["array"].dtype == np.float32


def test_load_nifti_volume_missing_file_raises(tmp_path):
    missing = tmp_path / "does_not_exist.nii.gz"
    with pytest.raises(FileNotFoundError):
        load_nifti_volume(str(missing))


def test_extract_slice_each_axis():
    volume = np.arange(4 * 5 * 6, dtype=np.float32).reshape(4, 5, 6)
    s0 = extract_slice(volume, axis=0, index=2)
    assert s0.shape == (5, 6)

    s1 = extract_slice(volume, axis=1, index=2)
    assert s1.shape == (4, 6)

    s2 = extract_slice(volume, axis=2, index=3)
    assert s2.shape == (4, 5)


def test_extract_slice_clamps_out_of_range():
    volume = np.zeros((4, 4, 4), dtype=np.float32)
    s = extract_slice(volume, axis=0, index=-5)
    assert s.shape == (4, 4)
    s = extract_slice(volume, axis=0, index=999)
    assert s.shape == (4, 4)


def test_extract_slice_bad_axis_raises():
    volume = np.zeros((4, 4, 4), dtype=np.float32)
    with pytest.raises(ValueError):
        extract_slice(volume, axis=5, index=0)


def test_middle_slice_index():
    volume = np.zeros((10, 20, 30), dtype=np.float32)
    assert middle_slice_index(volume, axis=0) == 5
    assert middle_slice_index(volume, axis=1) == 10
    assert middle_slice_index(volume, axis=2) == 15