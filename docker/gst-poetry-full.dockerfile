ARG GST_DOCKER_IMAGE_PREFIX="ghcr.io/gamestonkterminal"
ARG GST_DOCKER_POETRY_FULL_DEPS_VERSION="1.2.0"
FROM ${GST_DOCKER_IMAGE_PREFIX}/gst-poetry-full-deps:${GST_DOCKER_POETRY_FULL_DEPS_VERSION}

COPY --chown=python:python . .

CMD ["bash", "docker/entry-point-poetry.sh"]
