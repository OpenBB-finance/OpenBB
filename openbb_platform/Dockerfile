# syntax=docker/dockerfile:1
#
# Build context must be the repository root (not openbb_platform/), since
# dev_install.py installs packages from both openbb_platform/ and cli/:
#   docker build -f openbb_platform/Dockerfile -t openbb-platform .
#
# Installs every tracked package editable from this checkout via
# openbb_platform/dev_install.py.

FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

COPY . .

RUN python openbb_platform/dev_install.py --routers

FROM python:3.11-slim

RUN useradd --create-home --shell /bin/bash openbb

COPY --from=builder /usr/local /usr/local
COPY --from=builder --chown=openbb:openbb /app /app

USER openbb
ENV HOME=/home/openbb
ENV PYTHONUNBUFFERED=1
ENV OPENBB_CONFIG=/app/openbb_platform/openbb.docker.toml

WORKDIR /app/openbb_platform

EXPOSE 6900 8001

CMD ["openbb-api"]
