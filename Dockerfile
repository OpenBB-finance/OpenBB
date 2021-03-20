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
bzip2 \ 
libsm6 \ 
libxt6 \ 
libgl1-mesa-glx \ 
libpng16-16 \
python3-tk && \
apt-get -y autoremove && \
apt-get clean && \
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN useradd --create-home --shell /bin/bash python
USER python
WORKDIR /home/python

ENV PATH="/home/python/.local/bin:${PATH}"

COPY --chown=python:python . .

#RUN INSTALL_ON_LINUX=1 pip install -r requirements.txt
RUN pip install "poetry==1.1.4"
RUN poetry export --without-hashes -f requirements.txt | pip install -r /dev/stdin

CMD ["python", "terminal.py"]
