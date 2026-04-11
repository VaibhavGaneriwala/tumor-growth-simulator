# Author: Vaibhav Ganeriwala
# Description: Growth functions for the core module.

import math

def simulate_exponential(v0, k, days):
    """Simulates exponential growth."""
    days_list = []
    volumes_list = []
    for t in range(days + 1):
        volume = v0 * math.exp(k * t)
        days_list.append(t)
        volumes_list.append(volume)
    return days_list, volumes_list

def simulate_linear(v0, slope, days):
    """Simulates linear growth."""
    days_list = []
    volumes_list = []
    for t in range(days + 1):
        volume = v0 + slope * t
        if volume < 0:
            volume = 0
        days_list.append(t)
        volumes_list.append(volume)
    return days_list, volumes_list

def simulate_gompertz(v0, k, carrying_cap, days):
    """Simulates Gompertz growth."""
    if v0 <= 0 or carrying_cap <= 0:
        return list(range(days + 1)), [0.0 for _ in range(days + 1)]
    
    log_ratio = math.log(v0 / carrying_cap)
    days_list = []
    volumes_list = []
    for t in range(days + 1):
        volume = carrying_cap * math.exp(log_ratio * math.exp(-k * t))
        days_list.append(t)
        volumes_list.append(volume)
    return days_list, volumes_list

def simulate_with_scenario(v0, k, days, treatment_start_day=None, post_treatment_k=None):
    """Simulates growth with an optional treatment scenario."""
    days_list = []
    volumes_list = []
    current_volume = v0

    for t in range(days + 1):
        if t == 0:
            volume = v0
        else:
            if treatment_start_day is not None and t >= treatment_start_day and post_treatment_k is not None:
                rate = post_treatment_k
            else:
                rate = k
            volume = current_volume * math.exp(rate)
            if volume < 0:
                volume = 0

        days_list.append(t)
        volumes_list.append(volume)
        current_volume = volume
    return days_list, volumes_list