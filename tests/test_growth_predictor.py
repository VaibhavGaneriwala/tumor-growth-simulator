# Author: Vaibhav Ganeriwala
# Description: Unit tests for src/ml/growth_predictor.py

from unittest.mock import patch
from src.ml import growth_predictor


def test_is_model_available_returns_bool():
    """is_model_available should always return a Python bool."""
    result = growth_predictor.is_model_available()
    assert isinstance(result, bool)

def test_predict_returns_none_when_model_missing():
    """If the model file isn't on disk, predict_growth_rate should return None instead of raising an exception."""
    with patch.object(growth_predictor, "is_model_available", return_value=False):
        growth_predictor._cached_model = None
        result = growth_predictor.predict_growth_rate(age=60, sex="Female", initial_volume_mm3=1_000_000)
        assert result is None


def test_predict_with_mocked_model_returns_float():
    """When a model is available, predict_growth_rate should return a float."""
    class FakeModel:
        def predict(self, features):
            return [0.0023]

    with patch.object(growth_predictor, "_cached_model", FakeModel()):
        result = growth_predictor.predict_growth_rate(age=70, sex="Male", initial_volume_mm3=900_000)
        assert isinstance(result, float)
        assert result == 0.0023


def test_predict_handles_various_sex_inputs():
    """The wrapper should accept Male/Female strings AND 0/1 ints AND unknowns without crashing — and the encoded value should reach the model."""
    captured_features = []

    class CapturingModel:
        def predict(self, features):
            captured_features.append(features[0])
            return [0.001]

    with patch.object(growth_predictor, "_cached_model", CapturingModel()):
        growth_predictor.predict_growth_rate(60, "Female", 1_000_000)
        growth_predictor.predict_growth_rate(60, "Male", 1_000_000)
        growth_predictor.predict_growth_rate(60, 1, 1_000_000)
        growth_predictor.predict_growth_rate(60, 0, 1_000_000)
        growth_predictor.predict_growth_rate(60, "??", 1_000_000)

    sex_encoded_values = [features[1] for features in captured_features]
    assert sex_encoded_values == [1.0, 0.0, 1.0, 0.0, 1.0]