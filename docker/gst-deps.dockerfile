ARG GST_DOCKER_IMAGE_PREFIX="ghcr.io/gamestonkterminal"
ARG GST_DOCKER_PYTHON_VERSION="1.0.0"
FROM ${GST_DOCKER_IMAGE_PREFIX}/gst-python:${GST_DOCKER_PYTHON_VERSION}

COPY --chown=python:python requirements.txt /home/python/

RUN pip install -r requirements.txt
