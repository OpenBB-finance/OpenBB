ARG OPENBBTERMINAL_DOCKER_IMAGE_PREFIX="ghcr.io/openbb-finance"
ARG OPENBBTERMINAL_DOCKER_POETRY_FULL_DEPS_VERSION="1.2.0"
FROM ${OPENBBTERMINAL_DOCKER_IMAGE_PREFIX}/openbbterminal-poetry-full-deps:${OPENBBTERMINAL_DOCKER_POETRY_FULL_DEPS_VERSION}

LABEL org.opencontainers.image.source https://github.com/OpenBB-finance/OpenBBTerminal

COPY --chown=python:python . .

CMD ["bash", "docker/entry-point-poetry.sh"]
