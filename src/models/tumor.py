# Author: Vaibhav Ganeriwala
# Description: Tumor class for Tumor Growth Simulator

import math
import numpy as np

class Tumor:
    """
    Represents total tumor burden over time for a single patient.
    """

    def __init__(self, patient_id, measurements=None):
        self.patient_id = patient_id
        self.measurements = list(measurements) if measurements else []

    def add_measurement(self, when, volume_mm3):
        """Append a single (datetime, volume) measurement to the time series."""
        self.measurements.append((when, float(volume_mm3)))

    def num_measurements(self):
        """Return how many measurements are stored."""
        return len(self.measurements)
    
    def get_sorted_measurements(self):
        """Return measurements sorted by datetime"""
        return sorted(self.measurements, key=lambda m: m[0])
    
    def latest_volume(self):
        """Return the most recent volume in mm3 or None if empty"""
        if not self.measurements:
            return None
        sorted_m = self.get_sorted_measurements()
        return sorted_m[-1][1]
    
    def get_timeseries(self):
        """Return 2 parallel lists (dates and volumes) sorted by date.
        """
        sorted_m = self.get_sorted_measurements()
        dates = [m[0] for m in sorted_m]
        volumes = [m[1] for m in sorted_m]
        return dates, volumes
    
    def days_since_first(self):
        """Return a list of day offsets from the first measurement"""
        if not self.measurements:
            return []
        sorted_m = self.get_sorted_measurements()
        first_date = sorted_m[0][0]
        offsets = []
        for when, _ in sorted_m:
            delta = when - first_date
            offsets.append(delta.total_seconds() / 86400.0)
        return offsets
    
    def estimate_growth_rate(self):
        """Fit an exponenetial model V = V0 * exp(k*t) to measurements and return growth rate k (per day)"""
        if self.num_measurements() < 2:
            return None

        days_all = self.days_since_first()
        _, volumes_all = self.get_timeseries()

        valid = [(d, v) for d, v in zip(days_all, volumes_all) if v > 0]
        if len(valid) < 2:
            return None

        days = [d for d, _ in valid]
        log_volumes = [math.log(v) for _, v in valid]

        slope, _intercept = np.polyfit(days, log_volumes, 1)
        return float(slope)
    
    def __repr__(self):
        return (
            f"Tumor(patient_id={self.patient_id!r}, "
            f"measurements={self.num_measurements()})"
        )