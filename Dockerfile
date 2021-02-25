FROM python:3.6.13-slim-buster

RUN apt-get update && apt-get -y install --no-install-recommends \
ca-certificates \
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
apt-get clean && \
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN useradd --create-home --shell /bin/bash python
USER python
WORKDIR /home/python

COPY . .

RUN INSTALL_ON_LINUX=1 pip install -r requirements.txt
RUN pip install git+https://github.com/DidierRLopes/TimeSeriesCrossValidation

# is there a better way to do this? The chown is quite slow!
USER root
RUN chown -R python:python /home/python
USER python

CMD ["python", "gamestonk_terminal.py"]
