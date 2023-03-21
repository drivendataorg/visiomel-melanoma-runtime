# VisioMel Challenge: Predicting Melanoma Relapse

### For instructions about how to submit to the [VisioMel Challenge: Predicting Melanoma Relapse](https://www.drivendata.org/competitions/148/visiomel/), start with the [code submission format page](https://www.drivendata.org/competitions/148/visiomel/page/719/) of the competition website.

Welcome to the runtime repository for the [VisioMel Challenge: Predicting Melanoma Relapse](https://www.drivendata.org/competitions/148/visiomel/)! This repository contains the definition of the environment where your code submissions will run. It specifies both the operating system and the software packages that will be available to your solution.

This repository has three primary uses for competitors:

:bulb: **Provide example solutions**: You can find an examples to help you develop your solution. The [random baseline solution](https://github.com/drivendataorg/visiomel-melanoma-runtime/tree/main/examples_src/random_baseline) contains minimal code that runs succesfully in the runtime environment output and outputs a proper submission. This simply generates a random probability between zero and one for each tif. You can use this as a guide to bring in your model and generate a submission.

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
### [2. Troubleshooting](#troubleshooting)
 - [Downloading pre-trained weights](#downloading-pre-trained-weights)
 - [CPU and GPU](#cpu-and-gpu)
### [3. Updating runtime packages](#updating-runtime-packages)

----

## Getting started

### Prerequisites

 - A clone of this repository
 - [Docker](https://docs.docker.com/get-docker/)
 - At least 13 GB of free space for both the sample data and Docker images
 - [GNU make](https://www.gnu.org/software/make/) (optional, but useful for running the commands in the Makefile)

Additional requirements to run with GPU:

 - [NVIDIA drivers](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html#package-manager-installation) with **CUDA 11**
 - [NVIDIA Docker container runtime](https://nvidia.github.io/nvidia-container-runtime/)

### Simulating test data

In the official code execution platform, `code_execution/data` will contain the _actual test data_, which no participants have access to, and this is what will be used to compute your score for the leaderboard.

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

Your final submission should be a zip archive named with the extension `.zip` (for example, `submission.zip`). The root level of the `submission.zip` file must contain a `main.py` which performs inference on the test images and writes the predictions to a file named `submission.csv` in the same directory as `main.py`.

For more detail, see the "what to submit" section of the [code submission page](https://www.drivendata.org/competitions/148/visiomel/page/719/#what-to-submit).

Here's a few **do**s and **don't**s:

**Do**:
- Include a `main.py` in the root directory of your submission zip. There can be extra files with more code that is called.
- Include any model weights in your submission zip as there will be no network access.
- Write out a `submissions.csv` to the root directory when inference is finished, matching the submission format exactly.
- Log general information that will help you debug your submission.
- Test your submission locally and using the smoke test functionality on the platform.
- Consider ways to optimize your pipeline so that it runs end-to-end in under 8 hours.

**Don't**:
- Read from locations other than your solution directory.
- Use information from other images in the test set in making a prediction for a given tif file.
- Print or log any information about the test metadata or test images, including specific data values and aggregations such as sums, means, or counts.

**Participants who violate the rules will be subject for disqualification from the competition.**

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
   
> ⚠️ **Remember** that `code_execution/data` is just a mounted version of what you have saved locally in `data` so you will just be using the publicly available training files for local testing. In the official code execution platform, `code_execution/data` will contain the _actual test data_, which no participants have access to, and this is what will be used to compute your score for the leaderboard.

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

Thanks for reading! Enjoy the competition, and [hit up the forum](https://community.drivendata.org/) if you have any questions!

