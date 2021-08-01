FROM gst/gst-python:1.0.0

COPY --chown=python:python requirements.txt /home/python/

RUN pip install -r requirements.txt
