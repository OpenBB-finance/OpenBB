ARG OPENBBTERMINAL_DOCKER_IMAGE_PREFIX="ghcr.io/openbb-finance"
ARG OPENBBTERMINAL_DOCKER_PYTHON_VERSION="1.0.0"
FROM ${OPENBBTERMINAL_DOCKER_IMAGE_PREFIX}/openbbterminal-python:${OPENBBTERMINAL_DOCKER_PYTHON_VERSION}

LABEL org.opencontainers.image.source https://github.com/OpenBB-finance/OpenBBTerminal

COPY --chown=python:python pyproject.toml poetry.lock /home/python/

RUN mkdir /home/python/openbb_terminal && \
  touch openbb_terminal/__init__.py && \
  chown python:python /home/python/openbb_terminal /home/python/openbb_terminal/__init__.py && \
  poetry install
