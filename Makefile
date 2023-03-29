.PHONY: build pull pack-example pack-submission test-submission _check_image _echo_image _submission_write_perms

#################################################################################
# Settings                                                                      #
#################################################################################

ifeq (, $(shell which nvidia-smi))
CPU_OR_GPU ?= cpu
else
CPU_OR_GPU ?= gpu
endif

TAG := ${CPU_OR_GPU}-latest
LOCAL_TAG := ${CPU_OR_GPU}-local

IMAGE_NAME = visiomelmelanoma-competition
OFFICIAL_IMAGE = visiomelmelanoma.azurecr.io/${IMAGE_NAME}
LOCAL_IMAGE = ${IMAGE_NAME}

# Resolve which image to use in commands. The priority is:
# 1. User-provided, e.g., SUBMISSION_IMAGE=my-image:gpu-local make test-submission
# 2. Local image, e.g., visiomelmelanoma-competition:gpu-local
# 3. Official competition image, e.g., visiomelmelanoma.azurecr.io/visiomelmelanoma-competition
SUBMISSION_IMAGE ?= ${LOCAL_IMAGE}:${LOCAL_TAG}
ifeq (,$(shell docker images -q ${SUBMISSION_IMAGE}))
SUBMISSION_IMAGE = ${OFFICIAL_IMAGE}:${TAG}
endif

# Get the image ID
SUBMISSION_IMAGE_ID := $(shell docker images -q ${SUBMISSION_IMAGE})

# Name of the running container, i.e., docker run ... --name <CONTAINER_NAME>
CONTAINER_NAME ?= visiomelmelanoma

# Enable or disable host GPU access
ifeq (${CPU_OR_GPU}, gpu)
GPU_ARGS = --gpus all
endif

SKIP_GPU ?= false
ifeq (${SKIP_GPU}, true)
GPU_ARGS =
endif

# If no TTY (for example GitHub Actions CI) no interactive tty commands for docker
ifneq (true, ${GITHUB_ACTIONS_NO_TTY})
TTY_ARGS = -it
endif

# Option to block or allow internet access from the submission Docker container
ifeq (true, ${BLOCK_INTERNET})
NETWORK_ARGS = --network none
endif

# Name of the example submission to pack when running `make pack-example`
EXAMPLE ?= benchmark

# Give write access to the submission folder to everyone so Docker user can write when mounted
_submission_write_perms:
	mkdir -p submission/
	chmod -R 0777 submission/


_check_image:
# If container does not exist, error and tell user to pull or build
ifeq (${SUBMISSION_IMAGE_ID},)
	$(error To test your submission, you must first run `make pull` (to get official container) or `make build` \
		(to build a local version if you have changes).)
endif

_echo_image:
	@echo
ifeq (,${SUBMISSION_IMAGE_ID})
	@echo "$$(tput bold)Using image:$$(tput sgr0) ${SUBMISSION_IMAGE} (image does not exist locally)"
	@echo
else
	@echo "$$(tput bold)Using image:$$(tput sgr0) ${SUBMISSION_IMAGE} (${SUBMISSION_IMAGE_ID})"
	@echo "┏"
	@echo "┃ NAME(S)"
	@docker inspect $(SUBMISSION_IMAGE_ID) --format='{{join .RepoTags "\n"}}' | awk '{print "┃ "$$0}'
	@echo "└"
	@echo
endif
ifeq (,$(shell docker images ${OFFICIAL_IMAGE} -q))
	@echo "$$(tput bold)No official images available locally$$(tput sgr0)"
	@echo "Run 'make pull' to download the official image."
	@echo
else
	@echo "$$(tput bold)Available official images:$$(tput sgr0)"
	@echo "┏"
	@docker images ${OFFICIAL_IMAGE} | awk '{print "┃ "$$0}'
	@echo "└"
	@echo
endif
ifeq (,$(shell docker images ${LOCAL_IMAGE} -q))
	@echo "$$(tput bold)No local images available$$(tput sgr0)"
	@echo "Run 'make build' to build the image."
	@echo
else
	@echo "$$(tput bold)Available local images:$$(tput sgr0)"
	@echo "┏"
	@docker images ${LOCAL_IMAGE} | awk '{print "┃ "$$0}'
	@echo "└"
	@echo
endif

#################################################################################
# Commands for building the container if you are changing the requirements      #
#################################################################################

## Builds the container locally
build:
	docker build --build-arg CPU_OR_GPU=${CPU_OR_GPU} -t ${LOCAL_IMAGE}:${LOCAL_TAG} runtime

## Ensures that your locally built container can import all the Python packages successfully when it runs
test-container: _check_image _echo_image _submission_write_perms
	docker run \
		${GPU_ARGS} \
		${TTY_ARGS} \
		--mount type=bind,source="$(shell pwd)"/runtime/tests,target=/tests,readonly \
		--pid host \
		--entrypoint /bin/bash \
		${SUBMISSION_IMAGE_ID} \
		-c "conda run --no-capture-output -n condaenv python -m pytest tests"

## Open an interactive bash shell within the running container (with network access)
interact-container: _check_image _echo_image _submission_write_perms
	docker run \
		${GPU_ARGS} \
		--mount type=bind,source="$(shell pwd)"/data,target=/code_execution/data,readonly \
		--mount type=bind,source="$(shell pwd)"/submission,target=/code_execution/submission \
		--shm-size 8g \
		--pid host \
		-it \
		--entrypoint /bin/bash \
		${SUBMISSION_IMAGE_ID}

## Pulls the official container from Azure Container Registry
pull:
	docker pull ${OFFICIAL_IMAGE}:${TAG}

## Creates a submission/submission.zip file from the source code in examples_src
pack-example:
# Don't overwrite so no work is lost accidentally
ifneq (,$(wildcard ./submission/submission.zip))
	$(error You already have a submission/submission.zip file. Rename or remove that file (e.g., rm submission/submission.zip).)
endif
	mkdir -p submission/
	cd examples_src/${EXAMPLE}; zip -r ../../submission/submission.zip ./*

## Creates a submission/submission.zip file from the source code in submission_src
pack-submission:
# Don't overwrite so no work is lost accidentally
ifneq (,$(wildcard ./submission/submission.zip))
	$(error You already have a submission/submission.zip file. Rename or remove that file (e.g., rm submission/submission.zip).)
endif
	mkdir -p submission/
	cd submission_src; zip -r ../submission/submission.zip ./*

## Runs container using code from `submission/submission.zip` and data from `data/`
test-submission: _check_image _echo_image _submission_write_perms
# if submission file does not exist
ifeq (,$(wildcard ./submission/submission.zip))
	$(error To test your submission, you must first put a "submission.zip" file in the "submission" folder. \
	  If you want to use the benchmark, you can run `make pack-example <benchmark name>` first)
endif
	docker run \
		${TTY_ARGS} \
		${GPU_ARGS} \
		${NETWORK_ARGS} \
		--env "LOGURU_LEVEL=INFO" \
		--mount type=bind,source="$(shell pwd)"/data,target=/code_execution/data,readonly \
		--mount type=bind,source="$(shell pwd)"/submission,target=/code_execution/submission \
		--shm-size 8g \
		--pid host \
		--name ${CONTAINER_NAME} \
		--rm \
		${SUBMISSION_IMAGE_ID}

## Delete temporary Python cache and bytecode files
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

# Inspired by <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
# sed script explained:
# /^##/:
# 	* save line in hold space
# 	* purge line
# 	* Loop:
# 		* append newline + line to hold space
# 		* go to next line
# 		* if line starts with doc comment, strip comment character off and loop
# 	* remove target prerequisites
# 	* append hold space (+ newline) to line
# 	* replace newline plus comments by `---`
# 	* print line
# Separate expressions are necessary because labels cannot be delimited by
# semicolon; see <http://stackoverflow.com/a/11799865/1968>
.PHONY: help
help: _echo_image
	@echo
	@echo "$$(tput bold)Available commands:$$(tput sgr0)"
	@echo
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')
	@echo
