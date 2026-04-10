# Author: Vaibhav Ganeriwala
# Description: Unit tests for growth engine

import math
from src.core.growth import (simulate_exponential, simulate_gompertz, simulate_linear, simulate_with_scenario)

def test_exponential_known_values():
    days, volumes = simulate_exponential(1000, 0, 5)
    assert days == [0, 1, 2, 3, 4, 5]
    assert all(v == 1000 for v in volumes)

    days, volumes = simulate_exponential(1000, 0.01, 100)
    assert volumes[0] == 1000
    assert abs(volumes[-1] - 1000 * math.e) < 1e-6
    assert len(days) == 101

def test_linear_growth_and_negative_clamp():
    days, volumes = simulate_linear(100, 10, 5)
    assert volumes == [100, 110, 120, 130, 140, 150]

    days, volumes = simulate_linear(50, -20, 5)
    assert volumes[0] == 50
    assert volumes[-1] == 0
    assert all(v >= 0 for v in volumes)

def test_gompertz_approaches_carrying_cap():
    days, volumes = simulate_gompertz(v0=100, k=0.05, carrying_cap=5000, days=500)
    assert volumes[0] == 100
    assert volumes[-1] < 5000
    assert volumes[-1] > 4900
    for i in range(1, len(volumes)):
        assert volumes[i] >= volumes[i-1]

def test_gompertz_handles_bad_input():
    days, volumes = simulate_gompertz(v0=0, k=0.05, carrying_cap=5000, days=10)
    assert len(days) == 11
    assert all(v == 0.0 for v in volumes)

def test_scenario_treatment_changes_trajectory():
    days, volumes = simulate_with_scenario(v0=1000, k=0.02, days=60, treatment_start_day=30, post_treatment_k=-0.03)
    assert volumes[0] == 1000
    assert volumes[30] > 1000
    assert volumes[60] < volumes[30]
    assert len(days) == 61

def test_scenario_with_no_treatment_matches_exponential():
    days_a, volumes_a = simulate_with_scenario(v0=500, k=0.015, days=20)
    days_b, volumes_b = simulate_exponential(500, 0.015, 20)
    assert days_a == days_b
    for va, vb in zip(volumes_a, volumes_b):
        assert abs(va - vb) < 1e-9