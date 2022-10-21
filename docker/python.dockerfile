FROM python:3.9-slim-bullseye

LABEL org.opencontainers.image.source https://github.com/OpenBB-finance/OpenBBTerminal

RUN apt-get update
RUN apt-get -y install --no-install-recommends \
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
  python3-tk
RUN curl -sL https://deb.nodesource.com/setup_16.x -o nodesource_setup.sh
RUN bash nodesource_setup.sh
RUN apt-get install -y nodejs
RUN apt-get -y autoremove
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN useradd --create-home --shell /bin/bash python

USER python
WORKDIR /home/python

ENV PATH="/home/python/.local/bin:${PATH}"

RUN pip install "poetry==1.1.15"
