from pathlib import Path

import numpy as np
import pandas as pd


DATA_ROOT = Path(__file__).parent / "data"


def predict(filename):
    """Generate a random probability between 0 and 1."""
    return np.random.random()


def main():
    # load metadata
    metadata = pd.read_csv(DATA_ROOT / "test_metadata.csv", index_col=0)

    # load sumission format
    submission_format = pd.read_csv(DATA_ROOT / "submission_format.csv", index_col=0)

    # iterate over all images in the metdata
    for filename in metadata.filename:

        # prepend data path to image name
        filepath = DATA_ROOT / filename

        # make sure the image exists
        assert filepath.exists()

        # generate a prediction for that file
        pred = predict(filepath)

        # assign to the right row in the submission format
        submission_format.loc[filename, "relapse"] = pred

    # save as "submission.csv" in the root folder, where it is expected
    submission_format.to_csv("submission.csv")


if __name__ == "__main__":
    main()
