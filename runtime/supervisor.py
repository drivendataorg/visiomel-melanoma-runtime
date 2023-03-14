"""Main entrypoint script that supervises the participant's submission."""
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict

import pandas as pd
from config import (
    airports,
    data_directory,
    feature_names,
    prediction_directory,
    read_csv_kwargs,
    solution_directory,
    submission_format_path,
    submission_path,
)
from loguru import logger
from src.solution import load_model, predict

FEATURES = defaultdict(dict)

# censored features are slices of the entire feature data, disable assigning to them
pd.options.mode.chained_assignment = "raise"


def _load_features(airport: str, feature_name: str) -> pd.DataFrame:
    if feature_name in FEATURES[airport]:
        return FEATURES[airport][feature_name]
    else:
        FEATURES[airport][feature_name] = pd.read_csv(
            data_directory / airport / f"{airport}_{feature_name}.csv.bz2",
            **read_csv_kwargs[feature_name],
        )
        return FEATURES[airport][feature_name]


def _get_censored_features(airport: str, prediction_time: datetime) -> Dict[str, pd.DataFrame]:
    """Return the features for an airport. Handles reading the full feature tables from disk and
    using in-memory versions for subsequent calls."""

    gufis = set()
    censored_features = {}
    for feature_name in feature_names:
        if feature_name == "mfs":
            continue

        features = _load_features(airport, feature_name)
        censored_features[feature_name] = features.loc[
            (features.timestamp > (prediction_time - timedelta(hours=30)))
            & (features.timestamp <= prediction_time)
        ]

        if "gufi" in censored_features[feature_name]:
            gufis.update(set(censored_features[feature_name].gufi.tolist()))


    mfs = _load_features(airport, "mfs")
    censored_features["mfs"] = mfs.loc[mfs.gufi.isin(gufis)]

    return (
        censored_features["config"],
        censored_features["etd"],
        censored_features["first_position"],
        censored_features["lamp"],
        censored_features["mfs"],
        censored_features["runways"],
        censored_features["standtimes"],
        censored_features["tbfm"],
        censored_features["tfm"],
    )


def _check_partial_predictions(partial_submission_format, partial_predictions):
    if not partial_submission_format.drop(columns=["minutes_until_pushback"]).equals(
        partial_predictions.drop(columns=["minutes_until_pushback"])
    ):
        error_message = "Partial submission does not match expected format."

        missing_columns = partial_submission_format.columns.difference(partial_predictions.columns)
        if len(missing_columns):
            error_message += (
                f""" {len(missing_columns)} missing column(s) """
                f"""({", ".join(str(k) for k in missing_columns[:3])}...)."""
            )

        extra_columns = partial_predictions.columns.difference(partial_submission_format.columns)
        if len(extra_columns):
            error_message += (
                f""" {len(extra_columns)} extra column(s) """
                f"""({", ".join(str(k) for k in extra_columns[:3])}...)."""
            )

        missing_keys = partial_submission_format.index.difference(partial_predictions.index)
        if len(missing_keys):
            error_message += (
                f""" {len(missing_keys):,} missing indices """
                f"""({", ".join(str(k) for k in missing_keys[:3])}...)."""
            )

        extra_keys = partial_predictions.index.difference(partial_submission_format.index)
        if len(extra_keys):
            error_message += (
                f""" {len(extra_keys):,} extra indices """
                f"""({", ".join(str(k) for k in extra_keys[:3])}...)."""
            )
        raise KeyError(error_message)


def _log_progress(iterable, message: str, every: int):
    for i, item in enumerate(iterable):
        if (i % every) == 0:
            logger.info(message, i=i + 1, n=len(iterable), pct=i / len(iterable))
        yield item


def compute_predictions():
    model = load_model(solution_directory)
    submission_format = pd.read_csv(submission_format_path, parse_dates=["timestamp"])
    prediction_times = pd.to_datetime(submission_format.timestamp.unique()).sort_values()

    for prediction_time in _log_progress(
        prediction_times, message="Predicting {i} of {n} ({pct:.2%}) timestamps", every=10
    ):
        for airport in airports:
            (
                config,
                etd,
                first_position,
                lamp,
                mfs,
                runways,
                standtimes,
                tbfm,
                tfm,
            ) = _get_censored_features(airport, prediction_time)

            # partial submission format
            partial_submission_format = submission_format.loc[
                (submission_format.timestamp == prediction_time)
                & (submission_format.airport == airport)
            ].reset_index(drop=True)

            # call participant's predict function
            partial_predictions = predict(
                config,
                etd,
                first_position,
                lamp,
                mfs,
                runways,
                standtimes,
                tbfm,
                tfm,
                airport,
                prediction_time,
                partial_submission_format,
                model,
                solution_directory,
            )

            # check that partial predictions match partial submission format
            _check_partial_predictions(partial_submission_format, partial_predictions)

            partial_prediction_path = prediction_directory / f"{airport} {prediction_time}.csv"
            logger.debug(
                f"Writing partial predictions to {partial_prediction_path.relative_to(prediction_directory)}"
            )
            # save partial predictions
            partial_predictions.to_csv(
                partial_prediction_path, date_format="%Y-%m-%d %H:%M:%S", index=False
            )


def postprocess_predictions():
    logger.info("Concatenating partial predictions")
    submission = pd.concat(
        pd.read_csv(path, index_col=["gufi", "timestamp", "airport"])
        for path in prediction_directory.glob("*.csv")
    )

    logger.info("Reindexing submission to match submission format")
    submission_format = pd.read_csv(
        submission_format_path, index_col=["gufi", "timestamp", "airport"]
    )

    submission = submission.loc[submission_format.index]

    logger.info("Casting prediction to integer")
    submission["minutes_until_pushback"] = submission.minutes_until_pushback.astype(int)

    logger.info("Saving submission")
    submission.to_csv(submission_path, date_format="%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    if sys.argv[1] == "compute_predictions":
        compute_predictions()
    elif sys.argv[1] == "postprocess_predictions":
        postprocess_predictions()
