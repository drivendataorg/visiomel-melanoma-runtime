"""Predict a constant number of minutes to pushback."""
import json
from pathlib import Path
from typing import Any

import pandas as pd


def load_model(solution_directory: Path) -> Any:
    """Load any model assets from disk."""
    with (solution_directory / "model.json").open("r") as fp:
        model = json.load(fp)

    return model


def predict(
    config: pd.DataFrame,
    etd: pd.DataFrame,
    first_position: pd.DataFrame,
    lamp: pd.DataFrame,
    mfs: pd.DataFrame,
    runways: pd.DataFrame,
    standtimes: pd.DataFrame,
    tbfm: pd.DataFrame,
    tfm: pd.DataFrame,
    airport: str,
    prediction_time: pd.Timestamp,
    partial_submission_format: pd.DataFrame,
    model: Any,
    solution_directory: Path,
) -> pd.DataFrame:
    """Make predictions for the a set of flights at a single airport and prediction time."""
    return partial_submission_format.assign(minutes_until_pushback=model["minutes_until_pushback"])
