# Author: Vaibhav Ganeriwala
# Description: Train the growth-rate prediction model.

import csv
import math
import os
import random

import joblib
from sklearn.ensemble import RandomForestRegressor

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRAINING_CSV = os.path.join(_BASE_DIR, "models", "training_data.csv")
MODEL_OUTPUT_PATH = os.path.join(_BASE_DIR, "models", "growth_model.joblib")

RANDOM_SEED = 42
TEST_FRACTION = 0.2

N_ESTIMATORS = 50
MAX_DEPTH = 5
MIN_SAMPLES_LEAF = 10


def load_training_data(csv_path):
    """Read the CSV produced by dataset_builder and return parallel lists of feature vectors and target values."""
    feature_rows = []
    target_values = []

    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            features = [
                float(row["age"]),
                float(row["sex_encoded"]),
                float(row["initial_volume_mm3"]),
                float(row["num_visits"]),
                float(row["days_observed"]),
            ]
            target = float(row["growth_rate_k"])
            feature_rows.append(features)
            target_values.append(target)

    return feature_rows, target_values


def manual_train_test_split(features, targets, test_fraction, seed):
    """Manually shuffle and split into train/test."""
    n = len(features)
    indices = list(range(n))
    rng = random.Random(seed)
    rng.shuffle(indices)

    test_size = int(n * test_fraction)
    test_indices = indices[:test_size]
    train_indices = indices[test_size:]

    train_features = [features[i] for i in train_indices]
    train_targets = [targets[i] for i in train_indices]
    test_features = [features[i] for i in test_indices]
    test_targets = [targets[i] for i in test_indices]

    return train_features, train_targets, test_features, test_targets

def compute_mae(predictions, actuals):
    """Mean Absolute Error — manually with a loop."""
    if len(predictions) == 0:
        return 0.0
    total = 0.0
    for p, a in zip(predictions, actuals):
        total += abs(p - a)
    return total / len(predictions)


def compute_r2(predictions, actuals):
    """R² (coefficient of determination) — manually with loops."""
    if len(actuals) == 0:
        return 0.0

    mean_actual = sum(actuals) / len(actuals)

    ss_residual = 0.0
    ss_total = 0.0
    for p, a in zip(predictions, actuals):
        ss_residual += (a - p) ** 2
        ss_total += (a - mean_actual) ** 2

    if ss_total < 1e-12:
        return 0.0
    return 1.0 - (ss_residual / ss_total)


def main():
    print(f"Loading training data from {TRAINING_CSV}...")
    features, targets = load_training_data(TRAINING_CSV)
    print(f"Loaded {len(features)} samples.\n")

    train_x, train_y, test_x, test_y = manual_train_test_split(features, targets, TEST_FRACTION, RANDOM_SEED)

    print(f"Train set: {len(train_x)} samples")
    print(f"Test set:  {len(test_x)} samples\n")

    print("Training Random Forest Regressor...")
    model = RandomForestRegressor(n_estimators=N_ESTIMATORS, max_depth=MAX_DEPTH, min_samples_leaf=MIN_SAMPLES_LEAF, random_state=RANDOM_SEED,n_jobs=-1)
    model.fit(train_x, train_y)
    print("Training complete.\n")

    train_predictions = model.predict(train_x)
    train_mae = compute_mae(train_predictions, train_y)
    train_r2 = compute_r2(train_predictions, train_y)

    test_predictions = model.predict(test_x)
    test_mae = compute_mae(test_predictions, test_y)
    test_r2 = compute_r2(test_predictions, test_y)

    print("=== Performance ===")
    print(f"Train MAE: {train_mae:.6f}    Train R²: {train_r2:.4f}")
    print(f"Test  MAE: {test_mae:.6f}    Test  R²: {test_r2:.4f}\n")

    feature_names = ["age", "sex_encoded", "initial_volume_mm3", "num_visits", "days_observed"]
    importances = model.feature_importances_
    print("=== Feature importance ===")
    for name, importance in zip(feature_names, importances):
        print(f"  {name}: {importance:.4f}")
    print()

    joblib.dump(model, MODEL_OUTPUT_PATH)
    print(f"Model saved to {MODEL_OUTPUT_PATH}")

if __name__ == "__main__":
    main()