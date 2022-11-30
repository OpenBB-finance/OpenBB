###############################################
# Base Image openbb poetry build
###############################################
FROM --platform=linux/amd64 python:3.9-slim-bullseye as python

LABEL org.opencontainers.image.source https://github.com/OpenBB-finance/OpenBBTerminal

# PIP_DEFAULT_TIMEOUT: Set the default timeout for pip

ENV PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.1.15 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt" \
    VENV_PATH="/opt/.venv"

# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

###############################################
# Builder Image openbb poetry build
###############################################

FROM python as poetry-deps

RUN apt-get update

RUN apt-get install --no-install-recommends -y \
    curl \
    build-essential \
    unzip \
    git \
    python3-tk

RUN curl -sL https://deb.nodesource.com/setup_16.x -o nodesource_setup.sh
RUN bash nodesource_setup.sh
RUN apt-get install -y nodejs
RUN apt-get -y autoremove
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# install poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://install.python-poetry.org | python3 -

# copy project requirement files here to ensure they will be cached.
WORKDIR $PYSETUP_PATH

# Copy poetry files
COPY pyproject.toml website/content/sdk/quickstart/installation.md poetry.lock ./

RUN mkdir -p website/content/sdk/quickstart
RUN mkdir openbb_terminal
RUN mv installation.md ./website/content/sdk/quickstart
RUN touch openbb_terminal/__init__.py

# install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
RUN poetry install --no-dev --no-interaction -E optimization -E prediction

###############################################
# Production Image openbb poetry build
###############################################

FROM python as poetry

COPY --from=poetry-deps $PYSETUP_PATH $PYSETUP_PATH

WORKDIR $PYSETUP_PATH
COPY . .

RUN echo "OPENBB_LOGGING_APP_NAME=gst_docker" > .env

CMD ["python", "terminal.py"]
