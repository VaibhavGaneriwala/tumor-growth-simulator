# Author: Vaibhav Ganeriwala
# Description: Thin wrapper around the trained Random Forest growth-rate model.

import os
import joblib

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "models", "growth_model.joblib")

_cached_model = None

def is_model_available():
    """Return True if the trained model file exists on disk."""
    return os.path.exists(MODEL_PATH)

def load_model():
    """Load the trained Random Forest from disk. Cached after first call."""
    global _cached_model

    if _cached_model is not None:
        return _cached_model

    if not is_model_available():
        return None

    _cached_model = joblib.load(MODEL_PATH)
    return _cached_model


def predict_growth_rate(age, sex, initial_volume_mm3, num_visits=2, days_observed=180.0):
    """Predict an exponential growth rate (per day) for a patient."""
    model = load_model()
    if model is None:
        return None

    if sex == "Male" or sex == 0:
        sex_encoded = 0
    elif sex == "Female" or sex == 1:
        sex_encoded = 1
    else:
        return None

    features = [[
        float(age),
        float(sex_encoded),
        float(initial_volume_mm3),
        float(num_visits),
        float(days_observed),
    ]]

    prediction = model.predict(features)
    return float(prediction[0])