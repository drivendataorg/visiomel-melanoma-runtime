FROM nvidia/cuda:11.0.3-devel-ubuntu20.04
# This CUDA version does not matter
# We will separately install the CUDA runtime via cudatoolkit using conda

ARG CPU_OR_GPU=gpu

ENV CONDA_VERSION=22.11.1-4 \
    CONDA_ENV=condaenv \
    RUNTIME_USER=appuser \
    RUNTIME_UID=1000 \
    SHELL=/bin/bash \
    LANG=C.UTF-8  \
    LC_ALL=C.UTF-8 \
    CONDA_DIR=/opt/conda \
    DEBIAN_FRONTEND=noninteractive

ENV CPU_OR_GPU=${CPU_OR_GPU} \
    HOME=/home/${RUNTIME_USER} \
    PATH=${CONDA_DIR}/bin:${PATH}

# ======================== root ========================
# initialize paths we will use
RUN mkdir -p /code_execution

# Create appuser user, permissions, add conda init to startup script
RUN echo "Creating ${RUNTIME_USER} user..." \
    && groupadd --gid ${RUNTIME_UID} ${RUNTIME_USER}  \
    && useradd --create-home --gid ${RUNTIME_UID} --no-log-init --uid ${RUNTIME_UID} ${RUNTIME_USER} \
    && echo ". ${CONDA_DIR}/etc/profile.d/conda.sh ; conda activate ${CONDA_ENV}" > /etc/profile.d/init_conda.sh \
    && chown -R ${RUNTIME_USER}:${RUNTIME_USER} /opt /code_execution

# Install base packages
ARG DEBIAN_FRONTEND=noninteractive
COPY ./apt.txt /home/${RUNTIME_USER}
RUN echo "Installing base packages..." \
    && apt-get update --fix-missing \
    && apt-get install -y apt-utils 2> /dev/null \
    && xargs -a /home/${RUNTIME_USER}/apt.txt apt-get install -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /home/${RUNTIME_USER}/apt.txt

# ======================== user ========================
USER ${RUNTIME_USER}

# Install conda
RUN echo "Installing Miniforge..." \
    && URL="https://github.com/conda-forge/miniforge/releases/download/${CONDA_VERSION}/Miniforge3-${CONDA_VERSION}-Linux-x86_64.sh" \
    && wget --quiet ${URL} -O /home/${RUNTIME_USER}/miniconda.sh \
    && /bin/bash /home/${RUNTIME_USER}/miniconda.sh -u -b -p ${CONDA_DIR} \
    && rm /home/${RUNTIME_USER}/miniconda.sh \
    && conda install -y -c conda-forge mamba \
    && mamba clean -afy \
    && find ${CONDA_DIR} -follow -type f -name '*.a' -delete \
    && find ${CONDA_DIR} -follow -type f -name '*.pyc' -delete

COPY environment-${CPU_OR_GPU}.yml /home/${RUNTIME_USER}/environment.yml
RUN [ ${CPU_OR_GPU} = "gpu" ] && export CONDA_OVERRIDE_CUDA="11.0" || export CONDA_OVERRIDE_CUDA= \
    && mamba env create --name ${CONDA_ENV} -f /home/${RUNTIME_USER}/environment.yml  \
    && mamba clean -afy \
    && conda run pip cache purge \
    && rm /home/${RUNTIME_USER}/environment.yml \
    && find ${CONDA_DIR} -follow -type f -name '*.a' -delete \
    && find ${CONDA_DIR} -follow -type f -name '*.pyc' -delete \
    && find ${CONDA_DIR} -follow -type f -name '*.js.map' -delete

# ======================== ASAP installation ========================
USER root
RUN wget https://github.com/computationalpathologygroup/ASAP/releases/download/ASAP-2.1/ASAP-2.1-py310-Ubuntu2004.deb

RUN apt-get update \
    && seq 3 | xargs -i apt install -y libboost-program-options1.71.0 libboost-regex1.71.0 libdcmtk14 \
    && dpkg --install ASAP-2.1-py310-Ubuntu2004.deb || true \
    && apt-get -f install --fix-missing --fix-broken --assume-yes \
    && dpkg -i ASAP-2.1-py310-Ubuntu2004.deb \
    && ldconfig -v \
    && apt-get clean \
    && echo "/opt/ASAP/bin" > ${CONDA_DIR}/envs/${CONDA_ENV}/lib/python3.10/site-packages/asap.pth \
    && :

RUN rm ASAP-2.1-py310-Ubuntu2004.deb /usr/lib/x86_64-linux-gnu/libstdc++.so.6
RUN ln -s ${CONDA_DIR}/envs/${CONDA_ENV}/lib/libstdc++.so.6 /usr/lib/x86_64-linux-gnu/libstdc++.so.6
RUN ln -s ${CONDA_DIR}/envs/${CONDA_ENV}/lib/libpython3.10.so.1.0 /usr/lib/libpython3.10.so.1.0
USER ${RUNTIME_USER}
# ===================================================================

# ======================== MinkowskiEngine installation =============
USER root
ENV MAX_JOBS=2 \
    TORCH_CUDA_ARCH_LIST="6.0 6.1 7.0+PTX" \
    TORCH_NVCC_FLAGS="-Xfatbin -compress-all"
RUN git clone https://github.com/StanfordVL/MinkowskiEngine.git /tmp/MinkowskiEngine
WORKDIR /tmp/MinkowskiEngine
RUN if [ "$CPU_OR_GPU" = "gpu" ]; then \
      conda run -n ${CONDA_ENV} python setup.py install --force_cuda; \
    else \ 
      conda run -n ${CONDA_ENV} python setup.py install; \
    fi
WORKDIR /tmp
RUN rm -r MinkowskiEngine
USER ${RUNTIME_USER}
# ===================================================================

WORKDIR /code_execution

COPY entrypoint.sh /entrypoint.sh
COPY tests /code_execution/tests

CMD ["/bin/bash", "/entrypoint.sh"]
