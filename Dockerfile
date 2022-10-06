# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.10-bullseye

# install metadata-service
FROM python:$PYTHON_VERSION
COPY . /metadata-service
RUN python -m pip install --upgrade pip \
    && python -m pip install /metadata-service

# set workdir and entrypoint
WORKDIR /workdir
ENTRYPOINT ["python", "-m", "dataclay_mds.server"]
