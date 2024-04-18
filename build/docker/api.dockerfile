# ---- Base Python ----
FROM python:3.11-slim-bullseye AS base

# set work directory
WORKDIR /openbb

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential openssh-client curl libwebkit2gtk-4.0-dev \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# install toml and poetry
RUN pip install toml poetry

# ---- Copy Files/Build ----
FROM base AS builder

WORKDIR /openbb

COPY ./openbb_platform ./openbb_platform

# Install the SDK
RUN pip install /openbb/openbb_platform[all]

# ---- Copy Files ----
FROM base

COPY --from=builder /usr/local /usr/local

# Specify the command to run
CMD ["uvicorn", "openbb_core.api.rest_api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
