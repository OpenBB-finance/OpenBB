FROM python:3.8-slim-buster

LABEL org.opencontainers.image.source https://github.com/GamestonkTerminal/GamestonkTerminal

RUN  apt-get update && apt-get -y install --no-install-recommends \
  gcc \
  g++ \
  make \
  wget \
  curl \
  telnet \
  net-tools \
  iputils-ping \
  dnsutils \
  git \
  gnupg \
  unzip \
  bzip2 \
  libsm6 \
  libxt6 \
  libgl1-mesa-glx \
  libpng16-16 \
  procps \
  python3-tk && \
  curl -sL https://deb.nodesource.com/setup_14.x -o nodesource_setup.sh && \
  bash nodesource_setup.sh && \
  apt-get install -y nodejs && \
  apt-get -y autoremove && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN useradd --create-home --shell /bin/bash python

USER python
WORKDIR /home/python

ENV PATH="/home/python/.local/bin:${PATH}"

RUN pip install "poetry==1.1.11"
