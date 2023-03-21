# VisioMel Challenge: Predicting Melanoma Relapse

### For instructions about how to submit to the [VisioMel Challenge: Predicting Melanoma Relapse](https://www.drivendata.org/competitions/148/visiomel/), start with the [code submission format page](https://www.drivendata.org/competitions/148/visiomel/page/719/) of the competition website.

Welcome to the runtime repository for the [VisioMel Challenge: Predicting Melanoma Relapse](https://www.drivendata.org/competitions/148/visiomel/)! This repository contains the definition of the environment where your code submissions will run. It specifies both the operating system and the software packages that will be available to your solution.

This repository has three primary uses for competitors:

:bulb: **Provide example solutions**: You can find two examples to help you develop your solution.
1. [Baseline solution](https://github.com/drivendataorg/visiomel-melanoma-runtime/tree/main/examples_src/random_baseline): minimal code that runs succesfully in the runtime environment output and outputs a proper submission. This simply generates a random probability between zero and one for each tif. You can use this as a guide to bring in your model and generate a submission.
2. Implementation of the [benchmark solution](https://github.com/drivendataorg/visiomel-melanoma-runtime/tree/main/examples_src/random_forest_benchmark): submission code based on the [benchmark blog post](https://www.drivendata.co/blog/visiomel-melanoma-benchmark).

:wrench: **Test your submission**: Test your submission using a locally running version of the competition runtime to discover errors before submitting to the competition site. You can also find a [scoring script](https://github.com/drivendataorg/visiomel-melanoma-runtime/blob/main/scripts/score.py) implementing the competition metric.

:package: **Request new packages in the official runtime**: Since your submission will not be able to access the internet, all packages must be pre-installed. If you want to use a package that is not in the runtime environment, make a pull request to this repository. Make sure to test out adding the new package to both official environments, [CPU](https://github.com/drivendataorg/visiomel-melanoma-runtime/blob/main/runtime/environment-cpu.yml) and [GPU](https://github.com/drivendataorg/visiomel-melanoma-runtime/blob/main/runtime/environment-gpu.yml).

----


### [0. Getting started](#getting-started)
 - [Prerequisites](#prerequisites)
 - [Simulating test data](#simulating-test-data)
 - [Submission format](#code-submission-format)
### [1. Testing a submission locally](#testing-a-submission-locally)
 - [Running your submission locally](#running-your-submission-locally)
 - [Scoring your predictions](#scoring-your-predictions)
 - [Running the benchmark](#running-the-benchmark)
### [2. Troubleshooting](#troubleshooting)
 - [Downloading pre-trained weights](#downloading-pre-trained-weights)
 - [CPU and GPU](#cpu-and-gpu)
### [3. Updating runtime packages](#updating-runtime-packages)

----

## Getting started

### Prerequisites

 - A clone of this repository
 - [Docker](https://docs.docker.com/get-docker/)
 - At least 15 GB of free space for both the sample data and Docker images
 - [GNU make](https://www.gnu.org/software/make/) (optional, but useful for running the commands in the Makefile)

Additional requirements to run with GPU:

 - [NVIDIA drivers](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html#package-manager-installation) with **CUDA 11**
 - [NVIDIA Docker container runtime](https://nvidia.github.io/nvidia-container-runtime/)

### Simulating test data

To run a submission, the code execution environment reads images, metadata, and the submission format from the data directory on the host machine. The test set images and metadata are _only accessible in the runtime container_ and are mounted at `code_execution/data`.

To help you develop and debug your submissions, we provide a small sample of data with the same format. These files are created from the train set, but mimic the set up that you'll have in the runtime container.

Start by downloading `code_execution_development_data.tgz` from the [Data download page](https://www.drivendata.org/competitions/148/visiomel/data/). Unzip and extract the archive to `data` directory and you can develop and debug your submission on your local machine.

```
$ tree data
data
├── 8tn0wx0q.tif
├── qpbyhjj8.tif
├── submission_format.csv
├── test_labels.csv
└── test_metadata.csv
```

Note that in the runtime container, there will be around 500 tifs. And of course, there will not be a labels csv, which is included here for your use in scoring locally.

### Code submission format

Time is a key element in this competition―we're interested in a _real-time_ solution, one that can predict the future using only information available at the present. Assuring that a solution doesn't (accidentally or otherwise) use information from the future is complicated since the final evaluation dataset is a static dataset containing many different prediction times; a feature at 9 AM is valid for predicting 10 AM (it's in the past) but invalid for predicting 8 AM (it's in the future). In other words, each prediction time defines a unique set of valid features, different from that of all other prediction times! This makes it challenging to ensure that your submission only uses valid time points for each prediction time (and even more challenging for the competition hosts to validate that _all_ submissions are valid!).

The code execution runtime is designed to avoid the need to track valid and invalid features. It simulates real-time conditions for each prediction time and provides a simple way to access features that are guaranteed to be in the past. The process is defined in the [`runtime/supervisor.py`](https://github.com/drivendataorg/visiomel-melanoma-runtime/blob/main/runtime/supervisor.py), which runs the submissions. To summarize, for each prediction time in the submission format:

1. DrivenData's supervisor script, [**supervisor.py**](https://github.com/drivendataorg/visiomel-melanoma-runtime/blob/main/runtime/supervisor.py), calls your `load_model` function to load any assets (e.g., model weights) that will be needed for each prediction.
2. The supervisor creates an airport- and time-censored extract of the features, i.e., features from a single airport from 30 hours before the prediction time until the prediction time. It also creates a **partial submission format**, which is a subset of the submission format that only includes rows for the current airport and prediction time.
3. The supervisor calls your `predict` function passing along the censored features, the airport code, prediction time, model assets, and your solution directory.
4. Your `predict` function uses the provided censored features to compute predictions for the current prediction time for all the flights indicated in the partial submission format. It can use your model assets, any or all of the time-censored features in `/codeexecution/data`, the partial submission format, and it can load additional assets from your solution directory if needed.
5. Your `predict` function must return a pandas DataFrame that includes predicted minutes to pushback for the flights in the partial submission format. It should have the same format as the partial submission format with your predictions in the `minutes_until_pushback` column.
6. The supervisor checks that your predictions for this prediction time has the same indices and same columns as the partial submission format.

The supervisor repeats steps 2-6 for each airport and prediction time in order then combines all of the predictions into a single CSV, which is submitted to the platform for scoring.

Here's a few **do**s and **don't**s:

**Do**:
- Write a function `predict` that takes the censored features (`config`, `etd`, `first_position`, `lamp`, `mfs`, `runways`, `standtimes`, `tbfm`, `tfm`), airport code, prediction time, partial submission format, any model assets, and path to your solution directory.
- Use the features that the supervisor passes to your `predict` function at each call. These are guaranteed to be in the past relative to the prediction time.
- Return your pushback prediction times for all flights in the partial submission format that was passed to your `predict` function.
- Log general information that will help you debug your submission.
- Test your submission locally and using the smoke test functionality on the platform.
- Load your model in the `load_model` function to minimize repeated disk read.

**Don't**:
- Read from locations other than your solution directory.
- Write out files that can be used across calls to your `predict` function, for example caching features from previous time points.
- Print or log any information about the test features or test submission format, including specific data values and aggregations such as sums, means, or counts.

**Participants who violate these guidelines will be subject for disqualification from the competition.**

As long as you only use what the supervisor passes to your `predict` function, you can be sure your model isn't using information from the future. We provide the supervisor and utility scripts; all you need to do is provide the `predict` and `load_model` functions. We have included two sample solutions to help you get started:
- [`examples_src/30_min_to_pushback_benchmark`](https://github.com/drivendataorg/visiomel-melanoma-runtime/blob/main/examples_src/30_min_to_pushback_benchmark), which implements an extremely simple (but entirely valid) submission, predicting 30 minutes to pushback for all flights (a dreadful scenario).
- [`examples_src/fuser_etd_minus_15_min_benchmark`](https://github.com/drivendataorg/visiomel-melanoma-runtime/blob/main/examples_src/fuser_etd_minus_15_min_benchmark), which implements the _Fuser ETD minus 15 minutes_ solution from the [benchmark blog post](https://www.drivendata.co/blog/airport-pushback-benchmark).


## Testing a submission locally

When you make a submission on the DrivenData competition site, we run your submission inside a Docker container, a virtual operating system that allows for a consistent software environment across machines. **The best way to make sure your submission to the site will run is to first run it successfully in the container on your local machine.**

### Running your submission locally

This section provides instructions on how to run the your submission in the code execution container from your local machine. To simplify the steps, key processes have been defined in the `Makefile`. Commands from the `Makefile` are then run with `make {command_name}`. The basic steps are:

```
make pull
make pack-submission
make test-submission
```

Run `make help` for more information about the available commands as well as information on the official and built images that are available locally.

Here's the process in a bit more detail:

1. First, make sure you have set up the [prerequisites](#prerequisites).
2. [Download the code execution development dataset](#simulating-test-data) and extract it to `data`.
3. Download the official competition Docker image:

```
$ make pull
```

> Note that if you have built a local version of the runtime image with `make build`, that image will take precedence over the pulled image when using any make commands that run a container. You can explicitly use the pulled image by setting the `SUBMISSION_IMAGE` shell/environment variable to the pulled image or by deleting all locally built images.

4. Save all of your submission files, including the required `solution.py` script, in the `submission_src` folder of the runtime repository. Make sure any needed model weights and other assets are saved in `submission_src` as well.

5. Create a `submission/submission.zip` file containing your code and model assets:

```
$ make pack-submission 
mkdir -p submission/
cd submission_src; zip -r ../submission/submission.zip ./*
  adding: solution.py (deflated 73%)
```

6. Launch an instance of the competition Docker image, and run the same inference process that will take place in the official runtime:

```
$ make test-submission
```

This runs the container [entrypoint](https://github.com/drivendataorg/visiomel-melanoma-runtime/blob/main/runtime/entrypoint.sh), which unzips `submission/submission.zip` in the root directory of the container and runs the `main.py`script from your submission. In the local testing setting, the final submission is saved out to `submission/submission.csv` on your local machine.
   
> Remember that `code_execution/data` is a mounted version of what you have saved locally in `data`. In the official code execution platform, `code_execution/data` will contain the actual test images.

When you run `make test-submission` the logs will be printed to the terminal and written out to `submission/log.txt`. If you run into errors, use the `log.txt` to determine what changes you need to make for your code to execute successfully. For an example of what the logs look like when the full process runs successfully, see [`example_log.txt`](https://github.com/drivendataorg/visiomel-melanoma-runtime/blob/main/example_log.txt).

### Scoring your predictions

We have provided a [scoring script](https://github.com/drivendataorg/visiomel-melanoma-runtime/blob/main/scripts/score.py) to calculate the competition metric in the same way scores will be calculated in the DrivenData platform. The development dataset includes test labels, allowing you to score your predictions (although the actual scores won't be very meaningful).

1. After running your submission, the predictions generated by your code should be saved to `submission/submission.csv`.
2. Make sure the simulated test labels are saved in `data/test_labels.csv`.
3. Run `scripts/score.py` on your predictions:

```
$ python scripts/score.py
# TODO: update
2023-02-21 15:45:40.062 | SUCCESS  | __main__:main:15 - Score: 44.23704789833822
```

# TODO: remove benchmark section
### Running the benchmark

The code for the [benchmark](https://github.com/drivendataorg/visiomel-melanoma-runtime/blob/main/examples_src/fuser_etd_minus_15_min_benchmark/) is also provided as an example of how to structure a more complex submission. See the benchmark [blog post](https://www.drivendata.co/blog/airport-pushback-benchmark/) for a full walkthrough. The process to run the benchmark is the same as running your own submission, except that you will reference code in `examples_src` rather than `submission_src`.

```bash
make pull
make pack-example
make test-submission
```

Note that here we are running `pack-example` instead of `pack-submission`. Just like with your submission, the final predictions will be saved to `submission/submission.csv` on your local machine. You can also try out the `30_min_to_pushback_benchmark` by setting `EXAMPLE` when you run the make command:

```bash
EXAMPLE=30_min_to_pushback_benchmark make pack-example
```

## Troubleshooting

### Downloading pre-trained weights

Fine-tuning an existing model is common practice in machine learning. Many software packages will download the pre-trained model from the internet behind the scenes when you instantiate a model. That will fail in the the code execution environment, since submissions do not have open access to the internet. Instead you will need to include all weights along with your `submission.zip` and make sure that your code loads them from disk and rather than trying to download them from the internet.

For example, PyTorch uses a local cache which by default is saved to `~/.cache/torch`. Identify which of the weights in that directory are needed to run inference (if any), and copy them into your submission. If we need pre-trained ResNet34 weights we downloaded from online, we could run:

```sh
# Copy your local pytorch cache into submission_src/assets
cp ~/.cache/torch/checkpoints/resnet34-333f7ec4.pth submission_src/assets/

# Zip it all up in your submission.zip
zip -r submission.zip submission_src
```

When the platform runs your code, it will extract `assets` to `/code_execution/assets`. You'll need to tell PyTorch to use your custom cache directory instead of `~/.cache/torch` by setting the `TORCH_HOME` environment variable in your Python code (in `solution.py` for example).

```python
import os
os.environ["TORCH_HOME"] = "/code_execution/assets/torch"
```

Now PyTorch will load the model weights from the local cache, and your submission will run correctly in the code execution environment without internet access.

### CPU and GPU

The `make` commands will try to select the CPU or GPU image automatically by setting the `CPU_OR_GPU` variable based on whether `make` detects `nvidia-smi`.

**If you have `nvidia-smi` and a CUDA version other than 11**, you will need to explicitly set `make test-submission` to run on CPU rather than GPU. `make` will detect your GPU and automatically select the GPU image, but it will fail because `make test-submission` requires CUDA version 11. 
```bash
CPU_OR_GPU=cpu make pull
CPU_OR_GPU=cpu make test-submission
```

If you want to try using the GPU image on your machine but you don't have a GPU device that can be recognized, you can use `SKIP_GPU=true`. This will invoke `docker` without the `--gpus all` argument.

## Updating runtime packages

If you want to use a package that is not in the environment, you are welcome to make a pull request to this repository. If you're new to the GitHub contribution workflow, check out [this guide by GitHub](https://docs.github.com/en/get-started/quickstart/contributing-to-projects).

The runtime manages dependencies using [conda](https://docs.conda.io/en/latest/) environments. [Here is a good general guide](https://towardsdatascience.com/a-guide-to-conda-environments-bc6180fc533) to conda environments. The official runtime uses **Python 3.10.9** environments.

To submit a pull request for a new package:

1. Fork this repository.
   
2. Edit the [conda](https://docs.conda.io/en/latest/) environment YAML files, `runtime/environment-cpu.yml` and `runtime/environment-gpu.yml`. There are two ways to add a requirement:
    - Conda package manager **(preferred)**: Add an entry to the `dependencies` section. This installs from a conda channel using `conda install`. Conda performs robust dependency resolution with other packages in the `dependencies` section, so we can avoid package version conflicts.
    - Pip package manager: Add an entry to the `pip` section. This installs from PyPI using `pip`, and is an option for packages that are not available in a conda channel.

For both methods be sure to include a version, e.g., `numpy==1.20.3`. This ensures that all environments will be the same.

3. Locally test that the Docker image builds successfully for CPU and GPU images:

```sh
CPU_OR_GPU=cpu make build
CPU_OR_GPU=gpu make build
```

4. Commit the changes to your forked repository.
   
5. Open a pull request from your branch to the `main` branch of this repository. Navigate to the [Pull requests](https://github.com/drivendataorg/visiomel-melanoma-runtime/pulls) tab in this repository, and click the "New pull request" button. For more detailed instructions, check out [GitHub's help page](https://help.github.com/en/articles/creating-a-pull-request-from-a-fork).
   
6. Once you open the pull request, we will use Github Actions to build the Docker images with your changes and run the tests in `runtime/tests`. For security reasons, administrators may need to approve the workflow run before it happens. Once it starts, the process can take up to 30 minutes, and may take longer if your build is queued behind others. You will see a section on the pull request page that shows the status of the tests and links to the logs.
   
7. You may be asked to submit revisions to your pull request if the tests fail or if a DrivenData team member has feedback. Pull requests won't be merged until all tests pass and the team has reviewed and approved the changes.

---

## Good luck; have fun!

Thanks for reading! Enjoy the competition, and [hit up the forum](https://community.drivendata.org/c/pushback-to-the-future/92) if you have any questions!

