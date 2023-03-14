"""Predict 15 minutes before the Fuser estimated time of departure."""
import json
from pathlib import Path
from typing import Any

from loguru import logger
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
    logger.debug("Computing prediction based on Fuser ETD")

    latest_etd = etd.sort_values("timestamp").groupby("gufi").last().departure_runway_estimated_time
    departure_runway_estimated_time = partial_submission_format.merge(
        latest_etd, how="left", on="gufi"
    ).departure_runway_estimated_time

    prediction = partial_submission_format.copy()
    prediction["minutes_until_pushback"] = (
        (departure_runway_estimated_time - partial_submission_format.timestamp).dt.total_seconds()
        / 60
    ) - model["minutes_before_fuser_etd"]

    prediction["minutes_until_pushback"] = prediction.minutes_until_pushback.clip(lower=0).fillna(
        model["fillna_minutes"]
    )

    return prediction
