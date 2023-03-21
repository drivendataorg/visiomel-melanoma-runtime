from pathlib import Path

import pandas as pd
from loguru import logger
from sklearn.metrics import log_loss

REPO_ROOT = Path(__file__).parents[1]


def main():
    """Computes the log loss for provided predictions and labels."""
    predictions = pd.read_csv(REPO_ROOT / "submission" / "submission.csv")
    labels = pd.read_csv(REPO_ROOT / "data" / "test_labels.csv")
    score = log_loss(labels.relapse, predictions.relapse, eps=1e-16)
    logger.success(f"Score: {score}")


if __name__ == "__main__":
    main()
