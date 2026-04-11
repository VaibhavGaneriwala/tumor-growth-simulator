# Author: Mahera Sultana Shaik
# Description: Have functions for image processing

import cv2
import numpy as np

def normalize_to_uint8(slice_2d):
    """Normalize a 2D slice to the range [0, 255] and convert to uint8."""
    slice_float = slice_2d.astype(np.float32)
    slice_min = float(slice_float.min())
    slice_max = float(slice_float.max())

    if slice_max - slice_min < 1e-9:
        return np.zeros_like(slice_float, dtype=np.uint8)
    
    scaled = (slice_float - slice_min) / (slice_max - slice_min) * 255.0
    return scaled.astype(np.uint8)

def threshold_bright_regions(slice_2d_uint8, threshold):
    """Apply a threshold to identify bright regions in the 2D slice."""
    mask = (slice_2d_uint8 > threshold).astype(np.uint8) * 255
    return mask

def otsu_threshold(slice_2d_uint8):
    """Apply Otsu's thresholding to find an optimal threshold for bright regions."""
    chosen_threshold, mask = cv2.threshold(slice_2d_uint8, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return mask, float(chosen_threshold)

def estimate_mask_area_mm2(mask, voxel_dims_xy):
    """
    Estimate the real-world area of the masked region on a single 2D slice.
    """
    dx, dy = voxel_dims_xy
    pixel_count = int(np.sum(mask > 0))
    pixel_area_mm2 = dx * dy
    return pixel_count * pixel_area_mm2

def estimate_volume_mm3_from_slices(masks, voxel_dims):
    """Estimate total tumor volume in cubic millimeters by summing voxel contributions from each masked slice."""
    dx, dy, dz = voxel_dims
    voxel_volume = dx * dy * dz
    total_voxels = 0
    for mask in masks:
        total_voxels += int(np.sum(mask > 0))
    return total_voxels * voxel_volume

def enhance_contrast_clahe(slice_2d_uint8, clip_limit=2.0, tile_grid_size=(8, 8)):
    """Apply Contrast Limited Adaptive Histogram Equalization (CLAHE) to enhance local contrast in medical images."""
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    return clahe.apply(slice_2d_uint8)

def clean_mask_morphology(mask, kernel_size=3):
    """Clean up a binary mask by removing small speckles and filling small holes using morphological operations."""
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    opened = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    cleaned = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)
    return cleaned

def find_contours(mask, min_area=10):
    """Detect outlines of connected bright regions in a binary mask, filtering out contours smaller than `min_area` square pixels."""
    contours, _hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filtered = []
    for contour in contours:
        if cv2.contourArea(contour) >= min_area:
            filtered.append(contour)
    return filtered

def overlay_contours_on_slice(slice_2d_uint8, contours, thickness=2):
    """Draw the given contours on top of a grayscale slice and return a 3-channel color image with contours in bright red."""
    color_image = cv2.cvtColor(slice_2d_uint8, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(color_image, contours, contourIdx=-1, color=(0, 0, 255), thickness=thickness)
    return color_image

def process_slice_pipeline(slice_2d, threshold=180, threshold_mode="otsu", apply_clahe=True, clean_mask=True, min_contour_area=20):
    """Run the full tumor detection pipeline on a single 2D slice and return all intermediate results for GUI display."""
    normalized = normalize_to_uint8(slice_2d) 
    if apply_clahe:
        enhanced = enhance_contrast_clahe(normalized)
    else:
        enhanced = normalized.copy()
 
    if threshold_mode == "otsu":
        mask, threshold_used = otsu_threshold(enhanced)
    elif threshold_mode == "manual":
        mask = threshold_bright_regions(enhanced, threshold)
        threshold_used = float(threshold)
    else:
        raise ValueError(f"threshold_mode must be 'otsu' or 'manual' (got {threshold_mode!r})")
 
    if clean_mask:
        mask = clean_mask_morphology(mask)
 
    contours = find_contours(mask, min_area=min_contour_area) 
    overlay = overlay_contours_on_slice(enhanced, contours)
 
    return {
        "normalized": normalized,
        "enhanced": enhanced,
        "mask": mask,
        "contours": contours,
        "overlay": overlay,
        "num_regions": len(contours),
        "threshold_used": threshold_used,
    }