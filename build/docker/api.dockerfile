# ---- Base Python ----
FROM python:3.10-slim-buster AS base

# set work directory
WORKDIR /openbb

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential openssh-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ---- Copy Files/Build ----
FROM base AS builder

WORKDIR /openbb

COPY ./openbb_sdk ./openbb_sdk

# Install the SDK
RUN pip install /openbb/openbb_sdk

# ---- Copy Files ----
FROM base

COPY --from=builder /usr/local /usr/local

# Specify the command to run
CMD ["uvicorn", "openbb_core.api.rest_api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
