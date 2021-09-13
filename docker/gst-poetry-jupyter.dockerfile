ARG GST_DOCKER_IMAGE_PREFIX="ghcr.io/gamestonkterminal"
ARG GST_DOCKER_POETRY_FULL_DEPS_VERSION="1.2.0"
FROM ${GST_DOCKER_IMAGE_PREFIX}/gst-poetry-full-deps:${GST_DOCKER_POETRY_FULL_DEPS_VERSION}

LABEL org.opencontainers.image.source https://github.com/GamestonkTerminal/GamestonkTerminal

EXPOSE 8888

COPY --chown=python:python . .

RUN cp docker/lab-settings.json jupyterlab/gst-settings/schema/settings.json && \
  bash -x docker/extension.sh

CMD ["bash", "docker/entry-point-poetry-jupyter.sh"]
