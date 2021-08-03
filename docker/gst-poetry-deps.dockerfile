FROM gst/gst-python:1.0.0

COPY --chown=python:python pyproject.toml poetry.lock /home/python/

RUN mkdir /home/python/gamestonk_terminal && \
  touch gamestonk_terminal/__init__.py && \
  chown python:python /home/python/gamestonk_terminal /home/python/gamestonk_terminal/__init__.py && \
  poetry install
