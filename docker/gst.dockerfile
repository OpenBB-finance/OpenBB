ARG GST_DOCKER_IMAGE_PREFIX="ghcr.io/gamestonkterminal"
ARG GST_DOCKER_DEPS_VERSION="1.2.0"
FROM ${GST_DOCKER_IMAGE_PREFIX}/gst-deps:${GST_DOCKER_DEPS_VERSION}

COPY --chown=python:python . .

CMD ["bash", "docker/entry-point.sh"]
