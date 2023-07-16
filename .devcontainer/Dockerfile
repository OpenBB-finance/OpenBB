# SETUP PYTHON IMAGE
FROM --platform=linux/amd64 mcr.microsoft.com/vscode/devcontainers/python:0-3.10-bullseye AS python

LABEL org.opencontainers.image.source https://github.com/OpenBB-finance/OpenBBTerminal

# SETUP DEBIAN IMAGE
FROM python as debian

RUN apt-get update

RUN apt-get -y install --no-install-recommends \
    gcc \
    g++ \
    make

RUN apt-get -y install --no-install-recommends \
    git

RUN apt-get -y install --no-install-recommends \
    curl \
    wget

RUN apt-get -y install --no-install-recommends \
    libsm6 \
    libxt6 \
    libgl1-mesa-glx \
    libpng16-16 \
    libwebkit2gtk-4.0-dev \
    build-essential \
    libssl-dev \
    librsvg2-dev \
    ffmpeg \
    python3-tk

RUN apt-get clean

USER vscode
WORKDIR /home/vscode

# SETUP POETRY IMAGE
FROM debian as poetry

ENV PATH="/home/vscode/.local/bin:${PATH}"

# Define the version of Poetry to install (default is 1.4.2)
# Define the directory of python virtual environment
ARG PYTHON_VIRTUALENV_HOME=/home/vscode/openbb-py-env \
    POETRY_VERSION=1.4.0

ENV POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_NO_INTERACTION=true 

# Create a Python virtual environment for Poetry and install it
RUN python3 -m venv ${PYTHON_VIRTUALENV_HOME} && \
    $PYTHON_VIRTUALENV_HOME/bin/pip install --upgrade pip wheel && \
    $PYTHON_VIRTUALENV_HOME/bin/pip install poetry==${POETRY_VERSION}

ENV PATH="$PYTHON_VIRTUALENV_HOME/bin:$PATH" \
    VIRTUAL_ENV=$PYTHON_VIRTUALENV_HOME

# Setup for bash
RUN poetry completions bash >> /home/vscode/.bash_completion && \
    echo "export PATH=$PYTHON_VIRTUALENV_HOME/bin:$PATH" >> ~/.bashrc

# SETUP OPENBB IMAGE
FROM poetry as openbb-dev

COPY --chown=vscode:vscode pyproject.toml poetry.lock ./

RUN mkdir OpenBBUserData
RUN chown vscode:vscode OpenBBUserData

RUN mkdir .openbb_terminal
RUN chown vscode:vscode .openbb_terminal

RUN poetry install --no-root  --extras optimization --extras forecast

# Set the working directory for the app
WORKDIR /workspaces/openbb