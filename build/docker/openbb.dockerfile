# SETUP PYTHON IMAGE
FROM --platform=linux/amd64 python:3.10-slim-bullseye as python

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
    libgtk-3-dev \
    libayatana-appindicator3-dev \
    librsvg2-dev \
    ffmpeg \
    python3-tk

RUN apt-get clean

RUN useradd --create-home --shell /bin/bash python

USER python
WORKDIR /home/python

# SETUP POETRY IMAGE
FROM debian as poetry

RUN curl https://sh.rustup.rs -sSf | sh -s -- -y --default-toolchain nightly

ENV PATH="/home/python/.cargo/bin:${PATH}"
ENV PATH="/home/python/.local/bin:${PATH}"

RUN /bin/bash -c "source $HOME/.cargo/env"
RUN pip install --upgrade pip wheel
RUN pip install poetry==1.3.2

# SETUP OPENBB IMAGE
FROM poetry as repository

COPY --chown=python:python pyproject.toml poetry.lock terminal.py ./

RUN mkdir openbb_terminal
COPY --chown=python:python openbb_terminal openbb_terminal

RUN mkdir -p website/content/sdk
COPY --chown=python:python ./website/content/sdk/installation.md ./website/content/sdk

RUN mkdir OpenBBUserData
RUN chown python:python OpenBBUserData

RUN mkdir .openbb_terminal
RUN chown python:python .openbb_terminal

# SETUP OPENBB IMAGE
FROM repository as dependencies

RUN poetry install --no-root --no-dev --extras optimization --extras forecast

# SETUP OPENBB IMAGE
FROM dependencies as openbb

CMD ["poetry", "run", "python", "terminal.py"]
