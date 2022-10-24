ARG OPENBBTERMINAL_DOCKER_POETRY_DEPS_IMAGE="ghcr.io/openbb-finance/openbbterminal-poetry-deps:1.0.0"

FROM ${OPENBBTERMINAL_DOCKER_POETRY_DEPS_IMAGE}

LABEL org.opencontainers.image.source https://github.com/OpenBB-finance/OpenBBTerminal

COPY --chown=python:python . .

RUN poetry run python -m docker.make_env_file

CMD ["bash", "docker/entry-point-poetry.sh"]
