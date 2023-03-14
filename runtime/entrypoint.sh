#!/bin/bash

set -euxo pipefail

main () {
    expected_filename=solution.py

    cd /code_execution

    submission_files=$(zip -sf ./submission/submission.zip)
    if ! grep -q ${expected_filename}<<<$submission_files; then
        echo "Submission zip archive must include $expected_filename"
    return 1
    fi

    echo Installed packages
    echo "######################################"
    conda list -n nasa-pushback
    echo "######################################"

    echo Unpacking submission
    unzip ./submission/submission.zip -d ./src

    tree ./src

    echo "================ START TEST ================"
    conda run --no-capture-output -n nasa-pushback LOGURU_LEVEL=INFO python supervisor.py compute_predictions
    echo "================ END TEST ================"

    conda run --no-capture-output -n nasa-pushback python supervisor.py postprocess_predictions
}

main |& tee "/code_execution/submission/log.txt"
exit_code=${PIPESTATUS[0]}

cp /code_execution/submission/log.txt /tmp/log

exit $exit_code
