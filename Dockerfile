FROM python:3.6.13-slim-buster

RUN apt-get update && apt-get -y install --no-install-recommends \
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
bzip2 && \
apt-get -y autoremove && \
apt-get clean && \
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN useradd --create-home --shell /bin/bash python
USER python
WORKDIR /home/python

COPY --chown=python:python . .

RUN INSTALL_ON_LINUX=1 pip install -r requirements.txt

CMD ["python", "gamestonk_terminal.py"]
