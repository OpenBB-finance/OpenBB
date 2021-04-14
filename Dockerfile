# Build as: docker build . -t gamestonkterminal:dev
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

# TODO: fix matplotlib
# RUN echo 'backend      : TkAgg' >> ~/.config/matplotlib/matplotlibrc

ENV PATH="/home/python/.local/bin:${PATH}"

COPY --chown=python:python . .

RUN pip install -r requirements-full.txt

CMD ["python", "terminal.py"]
