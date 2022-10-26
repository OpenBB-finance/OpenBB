ARG OPENBBTERMINAL_DOCKER_PYTHON_IMAGE="ghcr.io/openbb-finance/openbbterminal-python:1.0.0"

FROM ${OPENBBTERMINAL_DOCKER_PYTHON_IMAGE}

LABEL org.opencontainers.image.source https://github.com/OpenBB-finance/OpenBBTerminal

COPY --chown=python:python pyproject.toml poetry.lock README.md /home/python/

RUN mkdir /home/python/openbb_terminal
RUN touch openbb_terminal/__init__.py
RUN chown python:python /home/python/openbb_terminal /home/python/openbb_terminal/__init__.py
RUN poetry install
