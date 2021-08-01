FROM gst/gst-deps:1.0.0

COPY --chown=python:python . .

CMD ["bash", "docker/entry-point.sh"]
