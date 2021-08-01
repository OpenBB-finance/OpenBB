FROM gst/gst-poetry-deps:1.0.0

COPY --chown=python:python . .

CMD ["bash", "docker/entry-point-poetry.sh"]
