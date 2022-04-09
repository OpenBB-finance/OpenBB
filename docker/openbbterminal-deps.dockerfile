ARG OPENBBTERMINAL_DOCKER_IMAGE_PREFIX="ghcr.io/openbb-finance"
ARG OPENBBTERMINAL_DOCKER_PYTHON_VERSION="1.0.0"
FROM ${OPENBBTERMINAL_DOCKER_IMAGE_PREFIX}/openbbterminal-python:${OPENBBTERMINAL_DOCKER_PYTHON_VERSION}

LABEL org.opencontainers.image.source https://github.com/OpenBB-finance/OpenBBTerminal

COPY --chown=python:python requirements.txt /home/python/

RUN pip install -r requirements.txt
