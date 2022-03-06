# Use Debian 11 as the base image. It's stable, reliable, and simple. Not the smallest, but it will work fine.
FROM debian:bullseye-slim

# Install git, Python, wget, and pip (the Python library manager)
RUN apt-get update && apt-get install git wget python3 python3-pip -y

# Download and uncrompress tarball
RUN mkdir GamestonkTerminal && wget https://github.com/GamestonkTerminal/GamestonkTerminal/tarball/master.tar.gz -O - | tar -xz -C GamestonkTerminal --strip-components 1
WORKDIR /GamestonkTerminal

# Download its dependicies using pip
RUN pip install -r requirements-full.txt && pip cache purge

# Create a little script to start the GamestonkTerminal
RUN printf '#!/bin/sh\npython3 /GamestonkTerminal/terminal.py\n' > /bin/run && chmod +x /bin/run

# Put our custom index.html and .gotty into the root directory of the container
COPY index.html /index.html

# I've built this version of gotty myself
# It uses the sources from here https://github.com/sorenisanerd/gotty
# Except the one difference is that font is hard-coded in
COPY gotty /bin/gotty
RUN chmod +x /bin/gotty

# And launch the script when we run the container
ENTRYPOINT gotty --index '/index.html' --term xterm --title-format 'Gamestonk Terminal Web' --permit-write run
