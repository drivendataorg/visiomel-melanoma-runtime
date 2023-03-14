from pathlib import Path

import pandas as pd
from loguru import logger
from sklearn.metrics import mean_absolute_error

REPO_ROOT = Path(__file__).parents[1]


def main():
    """Computes the mean absolute error for provided predictions and labels."""
    predictions = pd.read_csv(REPO_ROOT / "submission" / "submission.csv")
    labels = pd.read_csv(REPO_ROOT / "data" / "test_labels.csv")
    score = mean_absolute_error(labels.minutes_until_pushback, predictions.minutes_until_pushback)
    logger.success(f"Score: {score}")


if __name__ == "__main__":
    main()
