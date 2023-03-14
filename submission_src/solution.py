"""Solution for the NASA Pushback to the Future competition."""
from pathlib import Path
from typing import Any

import pandas as pd


def load_model(solution_directory: Path) -> Any:
    """Load any model assets from disk."""
    return


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
    """Make predictions for the a set of flights at a single airport and prediction time.

    Args:
        config (pd.DataFrame): The config table subset from 30 hours before the prediction time
            until the prediction time
        etd (pd.DataFrame): The etd table subset from 30 hours before the prediction time until the
            prediction time
        first_position (pd.DataFrame): The first_position table subset from 30 hours before the
            prediction time until the prediction time
        lamp (pd.DataFrame): The lamp table subset from 30 hours before the prediction time until
            the prediction time
        mfs (pd.DataFrame): The mfs table subset from 30 hours before the prediction time until the
            prediction time
        runways (pd.DataFrame): The runways table subset from 30 hours before the prediction time
            until the prediction time
        standtimes (pd.DataFrame): The standtimes table subset from 30 hours before the prediction
            time until the prediction time
        tbfm (pd.DataFrame): The tbfm table subset from 30 hours before the prediction time until
            the prediction time
        tfm (pd.DataFrame): The tfm table subset from 30 hours before the prediction time until the
            prediction time
        airport (str): Four-letter airport code of the airport to predict, e.g., KATL
        prediction_time (pd.Timestamp): The time at which predictions are made
        partial_submission_format (pd.DataFrame): A subset of the full submission format for which
            to make predictions. Includes the columns gufi, timestamp, airport,
            minutes_until_pushback
        model (Any): Model assets returned by your load_model function
        solution_directory (Path): Path to the directory containing your solution.py and model
            assets

    Returns:
        pd.DataFrame: Predictions for all of the flights in the partial_submission_format
    """
    return partial_submission_format
