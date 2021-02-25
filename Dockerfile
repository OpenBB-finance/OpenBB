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

RUN mkdir -p /home/gamestonkterminal
WORKDIR /home/gamestonkterminal

COPY . .

RUN INSTALL_ON_LINUX=1 && pip install -r requirements.txt
RUN pip install git+https://github.com/DidierRLopes/TimeSeriesCrossValidation

RUN chown -R python /home/gamestonkterminal
USER python

CMD ["python", "gamestonk_terminal.py"]
