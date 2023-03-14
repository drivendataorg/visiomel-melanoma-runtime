from pathlib import Path

airports = [
    "KATL",
    "KCLT",
    "KDEN",
    "KDFW",
    "KJFK",
    "KMEM",
    "KMIA",
    "KORD",
    "KPHX",
    "KSEA",
]

feature_names = [
    "config",
    "etd",
    "first_position",
    "lamp",
    "mfs",
    "runways",
    "standtimes",
    "tbfm",
    "tfm",
]


root_directory = Path("/code_execution")
data_directory = root_directory / "data"
submission_format_path = data_directory / "submission_format.csv"

solution_directory = root_directory / "src"
submission_path = root_directory / "submission" / "submission.csv"
prediction_directory = root_directory / "predictions"

read_csv_kwargs = {
    "config": {
        "dtype": {
            "departure_runways": str,
            "arrival_runways": str,
        },
        "parse_dates": [
            "timestamp",
            "start_time",
        ],
        "infer_datetime_format": True,
    },
    "etd": {
        "dtype": {
            "gufi": str,
        },
        "parse_dates": [
            "timestamp",
            "departure_runway_estimated_time",
        ],
        "infer_datetime_format": True,
    },
    "first_position": {
        "dtype": {"gufi": str},
        "parse_dates": ["timestamp"],
        "infer_datetime_format": True,
    },
    "lamp": {
        "dtype": {
            "temperature": float,
            "wind_direction": float,
            "wind_speed": float,
            "wind_gust": float,
            "cloud_ceiling": float,
            "visibility": float,
            "cloud": str,
            "lightning_prob": str,
            "precip": bool,
        },
        "parse_dates": [
            "timestamp",
            "forecast_timestamp",
        ],
        "infer_datetime_format": True,
    },
    "mfs": {
        "dtype": {
            "gufi": str,
            "aircraft_engine_class": str,
            "aircraft_type": str,
            "major_carrier": str,
            "flight_type": str,
            "isdeparture": bool,
        }
    },
    "runways": {
        "dtype": {
            "gufi": str,
            "departure_runway_actual": str,
            "arrival_runway_actual": str,
        },
        "parse_dates": [
            "timestamp",
            "departure_runway_actual_time",
            "arrival_runway_actual_time",
        ],
        "infer_datetime_format": True,
    },
    "standtimes": {
        "dtype": {
            "gufi": str,
        },
        "parse_dates": [
            "timestamp",
            "arrival_stand_actual_time",
            "departure_stand_actual_time",
        ],
        "infer_datetime_format": True,
    },
    "tbfm": {
        "dtype": {
            "gufi": str,
        },
        "parse_dates": [
            "timestamp",
            "scheduled_runway_estimated_time",
        ],
        "infer_datetime_format": True,
    },
    "tfm": {
        "dtype": {
            "gufi": str,
        },
        "parse_dates": [
            "timestamp",
            "arrival_runway_estimated_time",
        ],
        "infer_datetime_format": True,
    },
}
