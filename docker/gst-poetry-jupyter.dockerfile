ARG GST_DOCKER_IMAGE_PREFIX="ghcr.io/gamestonkterminal"
ARG GST_DOCKER_POETRY_DEPS_VERSION="1.2.0"
FROM ${GST_DOCKER_IMAGE_PREFIX}/gst-poetry-deps:${GST_DOCKER_POETRY_DEPS_VERSION}

LABEL org.opencontainers.image.source https://github.com/GamestonkTerminal/GamestonkTerminal

COPY --chown=python:python . .

CMD ["bash", "docker/entry-point-poetry-jupyter.sh"]
