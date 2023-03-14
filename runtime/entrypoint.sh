#!/bin/bash

set -euxo pipefail

main () {
    expected_filename=main.py

    cd /code_execution

    submission_files=$(zip -sf ./submission/submission.zip)
    if ! grep -q ${expected_filename}<<<$submission_files; then
        echo "ERROR: Submission zip archive must include $expected_filename"
    return 1
    fi

    echo Installed packages
    echo "######################################"
    conda list -n condaenv
    echo "######################################"

    echo Unpacking submission
    unzip ./submission/submission.zip -d ./src

    tree ./src

    echo "Running code submission with Python"
    conda run --no-capture-output -n condaenv python main.py
    echo "... finished"

    echo "================ END ================"
}

main |& tee "/code_execution/submission/log.txt"
exit_code=${PIPESTATUS[0]}

cp /code_execution/submission/log.txt /tmp/log

exit $exit_code
