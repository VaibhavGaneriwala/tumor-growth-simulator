# Author: Vaibhav Ganeriwala
# Description: Unit tests for the Tumor class.

import math
from datetime import datetime, timedelta

from src.models.tumor import Tumor


def test_empty_tumor():
    t = Tumor(patient_id="YG_TEST001")
    assert t.num_measurements() == 0
    assert t.latest_volume() is None
    assert t.days_since_first() == []
    assert t.estimate_growth_rate() is None


def test_add_and_sort_measurements():
    t = Tumor(patient_id="YG_TEST002")
    t.add_measurement(datetime(2020, 6, 1), 1500.0)
    t.add_measurement(datetime(2020, 1, 1), 1000.0)
    t.add_measurement(datetime(2020, 12, 1), 2200.0)

    assert t.num_measurements() == 3
    sorted_m = t.get_sorted_measurements()
    assert sorted_m[0][0] == datetime(2020, 1, 1)
    assert sorted_m[0][1] == 1000.0
    assert sorted_m[-1][0] == datetime(2020, 12, 1)
    assert t.latest_volume() == 2200.0


def test_get_timeseries_returns_parallel_lists():
    t = Tumor(patient_id="YG_TEST003")
    t.add_measurement(datetime(2021, 3, 1), 500.0)
    t.add_measurement(datetime(2021, 1, 1), 300.0)

    dates, volumes = t.get_timeseries()
    assert len(dates) == len(volumes) == 2
    assert dates[0] < dates[1]
    assert volumes == [300.0, 500.0]


def test_estimate_growth_rate_on_known_curve():
    t = Tumor(patient_id="YG_TEST004")
    start = datetime(2022, 1, 1)
    true_k = 0.01
    v0 = 1000.0
    for day in [0, 30, 60, 90, 120]:
        v = v0 * math.exp(true_k * day)
        t.add_measurement(start + timedelta(days=day), v)

    k = t.estimate_growth_rate()
    assert k is not None
    assert abs(k - true_k) < 1e-6


def test_estimate_growth_rate_handles_bad_data():
    t = Tumor(patient_id="YG_TEST005")
    t.add_measurement(datetime(2022, 1, 1), 1000.0)
    assert t.estimate_growth_rate() is None
    t.add_measurement(datetime(2022, 2, 1), 0.0)
    assert t.estimate_growth_rate() is None