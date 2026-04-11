# Author: Mahera Sultana Shaik
# Description: Unit tests for src/core/image_processing.py

import numpy as np
import pytest

from src.core.image_processing import (normalize_to_uint8, threshold_bright_regions, otsu_threshold, estimate_mask_area_mm2, estimate_volume_mm3_from_slices, enhance_contrast_clahe, clean_mask_morphology, find_contours, overlay_contours_on_slice, process_slice_pipeline)


def _make_slice_with_bright_blob(size=64, blob_center=(32, 32), blob_radius=8, background=50, blob_intensity=500):
    """Helper to create a synthetic 2D slice with a bright circular blob in the middle for testing."""
    slice_2d = np.full((size, size), background, dtype=np.float32)
    yy, xx = np.mgrid[0:size, 0:size]
    distance_from_center = np.sqrt((yy - blob_center[0]) ** 2 + (xx - blob_center[1]) ** 2)
    slice_2d[distance_from_center <= blob_radius] = blob_intensity
    return slice_2d


def test_normalize_to_uint8_basic():
    slice_2d = np.array([[0.0, 50.0], [100.0, 200.0]], dtype=np.float32)
    result = normalize_to_uint8(slice_2d)
    assert result.min() == 0
    assert result.max() == 255
    assert result.dtype == np.uint8


def test_normalize_to_uint8_flat_input():
    slice_2d = np.full((10, 10), 42.0, dtype=np.float32)
    result = normalize_to_uint8(slice_2d)
    assert result.shape == (10, 10)
    assert np.all(result == 0)


def test_threshold_bright_regions_produces_binary_mask():
    slice_uint8 = np.array([[10, 200], [50, 250]], dtype=np.uint8)
    mask = threshold_bright_regions(slice_uint8, threshold=100)
    assert mask[0, 0] == 0
    assert mask[0, 1] == 255
    assert mask[1, 0] == 0
    assert mask[1, 1] == 255
    assert mask.dtype == np.uint8


def test_estimate_mask_area_mm2():
    mask = np.zeros((10, 10), dtype=np.uint8)
    mask[0, 0:5] = 255
    area = estimate_mask_area_mm2(mask, voxel_dims_xy=(2.0, 3.0))
    assert area == 30.0


def test_estimate_volume_mm3_from_slices():
    m1 = np.zeros((5, 5), dtype=np.uint8)
    m1[0, 0:4] = 255
    m2 = np.zeros((5, 5), dtype=np.uint8)
    m2[1, 0:4] = 255
    volume = estimate_volume_mm3_from_slices([m1, m2], voxel_dims=(1.0, 1.0, 2.0))
    assert volume == 16.0


def test_clahe_preserves_shape_and_type():
    slice_uint8 = (np.random.rand(32, 32) * 255).astype(np.uint8)
    result = enhance_contrast_clahe(slice_uint8)
    assert result.shape == slice_uint8.shape
    assert result.dtype == np.uint8


def test_morphology_removes_isolated_speckle():
    mask = np.zeros((32, 32), dtype=np.uint8)
    mask[10:20, 10:20] = 255
    mask[0, 0] = 255
    cleaned = clean_mask_morphology(mask, kernel_size=3)
    assert cleaned[15, 15] == 255
    assert cleaned[0, 0] == 0


def test_find_contours_detects_single_blob():
    mask = np.zeros((32, 32), dtype=np.uint8)
    mask[10:20, 10:20] = 255
    contours = find_contours(mask, min_area=5)
    assert len(contours) == 1


def test_find_contours_filters_small_blobs():
    mask = np.zeros((64, 64), dtype=np.uint8)
    mask[10:30, 10:30] = 255
    mask[50, 50] = 255
    contours = find_contours(mask, min_area=10)
    assert len(contours) == 1


def test_overlay_contours_returns_3_channel():
    slice_uint8 = np.full((32, 32), 100, dtype=np.uint8)
    mask = np.zeros((32, 32), dtype=np.uint8)
    mask[10:20, 10:20] = 255
    contours = find_contours(mask)
    overlay = overlay_contours_on_slice(slice_uint8, contours)
    assert overlay.shape == (32, 32, 3)
    assert overlay.dtype == np.uint8


def test_pipeline_end_to_end_detects_synthetic_tumor():
    slice_2d = _make_slice_with_bright_blob(size=64, blob_center=(32, 32), blob_radius=8, background=50, blob_intensity=500)
    result = process_slice_pipeline(slice_2d, threshold=180, threshold_mode="manual", apply_clahe=False, clean_mask=True, min_contour_area=5)
    assert result["num_regions"] == 1
    assert result["normalized"].shape == (64, 64)
    assert result["mask"].shape == (64, 64)
    assert result["overlay"].shape == (64, 64, 3)
    assert int(np.sum(result["mask"] > 0)) > 0
    assert result["threshold_used"] == 180.0


def test_pipeline_clean_slice_detects_nothing():
    slice_2d = np.full((64, 64), 50.0, dtype=np.float32)
    result = process_slice_pipeline(slice_2d, threshold=180, threshold_mode="manual")
    assert result["num_regions"] == 0


def test_otsu_threshold_picks_sensible_value():
    slice_uint8 = np.zeros((64, 64), dtype=np.uint8)
    slice_uint8[:32, :] = 50
    slice_uint8[32:, :] = 200

    mask, chosen = otsu_threshold(slice_uint8)
    assert 50 <= chosen < 200
    assert mask[0, 0] == 0
    assert mask[50, 0] == 255


def test_pipeline_otsu_mode_detects_tumor():
    slice_2d = _make_slice_with_bright_blob(
        size=64, blob_center=(32, 32), blob_radius=8,
        background=50, blob_intensity=500,
    )
    result = process_slice_pipeline(slice_2d, threshold_mode="otsu", apply_clahe=False, clean_mask=True, min_contour_area=5)
    assert result["num_regions"] == 1
    assert 0 <= result["threshold_used"] <= 255
    assert int(np.sum(result["mask"] > 0)) > 0


def test_pipeline_invalid_mode_raises():
    slice_2d = np.zeros((16, 16), dtype=np.float32)
    with pytest.raises(ValueError):
        process_slice_pipeline(slice_2d, threshold_mode="bogus")