# OpenBBTerminal with Docker

Here are the steps to get OpenBBTerminal using the Docker containers that we provide:

1. Installing `Docker` and `Docker Compose`
2. Pulling and running `OpenBBTerminal Docker Container`
3. Configuring your X-server to show plots

Each of this steps need to be followed to have a working version of OpenBBTerminal.

We will detail these steps in the rest of this document.

## 1. Installing `Docker` and `Docker Compose`

**INSTALL DOCKER**

Installing Docker Desktop is the easiest way for most people:

It has a `Graphical User Interface` and comes with `Docke Compose` in it.

You can find `Docker Desktop` installation file for your `OS` here:

[Download Docker Desktop](https://www.docker.com/products/docker-desktop)

**START DOCKER**

Once you have `Docker` installed and running, you can use the following command to check the state:

```bash
docker info
```

It should output a text like this one:

```text
Client:
 Context:    default
 Debug Mode: false

Server:
 Containers: 14
  Running: 2
  Paused: 1
  Stopped: 10
...
```

If you see a message like the following, it most likely means you need to start `Docker`.

Open the docker desktop app in this case.

```text
Server:
ERROR: Cannot connect to the Docker daemon at unix:///var/run/docker.sock.
Is the docker daemon running?
```

## 2. Pulling and running `OpenBBTerminal Docker Container`

**DOCKER COMPOSE**

Here are the commands to use `Docker Compose` to pull and run the `OpenBBTerminal Docker Container`:

```bash
curl -o docker-compose.yaml https://raw.githubusercontent.com/OpenBB-finance/OpenBBTerminal/main/docker/docker-compose.yaml

docker compose run poetry
```

The command line with `curl` is downloading this file : [`docker-compose.yaml`](https://raw.githubusercontent.com/OpenBB-finance/OpenBBTerminal/main/docker/docker-compose.yaml).

The `docker-compose.yaml` file is a configuration file telling `Docker Compose`:

- where to find `OpenBBTerminal Docker Container`
- how to run this container.

The second command runs `Docker Compose` on the service `poetry` defined in this `docker-compose.yaml` file.

This second command must be run in the same folder in which `docker-compose.yaml` file is.

**DOCKER**

If you don't have `Docker Compose` you can also use `Docker` directly to run the `OpenBBTerminal Docker Container`.

Here is the commands to run:

```bash
docker pull ghcr.io/openbb-finance/openbbterminal-poetry:X.Y.Z

docker run -v ~/.openbb_terminal/:/home/python/.openbb_terminal -v ~/OpenBBUserData:/home/python/OpenBBUserData -it --rm ghcr.io/openbb-finance/openbbterminal-poetry:X.Y.Z
```

Be sure to replace `X.Y.Z` with the version you want to pull and run.

Note for windows:

```text
    Ignore this message if you are using Powershell or a more evolved interpreters. 
    If you are using the builtin Windows interpreter.
    Replace `~` by `%USERPROFILE%` in the command above.
```

## 3. Configuring your X-server to show plots

In order to display plots in the docker container, we need to configure the XServer on the host machine.
Without this configuration the interactive charts will not be displayed.

### On Windows

Download and install : [VcXsrv](https://sourceforge.net/projects/vcxsrv/)

When running the program is important to check "Disable access control"

Run `Docker Compose` like this:

```bash
curl -o docker-compose.yaml https://raw.githubusercontent.com/OpenBB-finance/OpenBBTerminal/main/docker/docker-compose.yaml

docker compose run poetry
```

Or run `Docker` directly:

```bash
docker run -v ~/.openbb_terminal:/home/python/.openbb_terminal -v ~/OpenBBUserData:/home/python/OpenBBUserData -it --rm --env DISPLAY=host.docker.internal:0.0 ghcr.io/openbb-finance/openbbterminal-poetry:X.Y.Z
```

### X-Server on macOS

Users familiar with Docker and X-Server can set the `DISPLAY` variable in the file [setenv](/docker/setenv) described above. If you use this approach remember to add `:0` at the end of your inet address. E.g. `DISPLAY=192.168.1.155:0`.

For help setting up the X-Server continue reading:

#### Setting up X Quartz/X11

On macOS the X11 client of choice is [XQuartz](https://www.xquartz.org/). On Windows it's [Xming](http://www.straightrunning.com/XmingNotes/). XQuartz will be used as an example further on.

0. Install X Quartz from <https://www.xquartz.org/>
1. With X Quartz open: go to Preferences -> Security and make sure both options are enabled.
   ![Screen Shot 2021-09-08 at 12 21 48 PM](https://user-images.githubusercontent.com/18151143/132548605-235d774b-9aa6-4a45-afcf-58fb775d376a.png)

#### Adding the display for Docker

From the command prompt or terminal, run the following to add your local configuration to the list of allowed access control:

```bash
IP=$(ifconfig | grep inet | grep -v -e "127.0.0.1" | awk '$1=="inet" {print $2}')
xhost + $IP
```

Now we can run the docker container, adding the display to the environment:

```bash
docker run -v ~/.openbb_terminal/:/home/python/.openbb_terminal -v ~/OpenBBUserData:/home/python/OpenBBUserData -it --rm --env-file=path/to/setenv --env DISPLAY=$IP:0 ghcr.io/openbb-finance/openbbterminal-poetry:X.Y.Z
```

This container will be able to display all the same plots as the terminal interface.

### X-Server on Linux Desktop

X-Server is default in Linux distribution. There is no need to install any clients.

#### Local docker container

We can use IPC socket to connect Desktop.

Add this setting to your `.env` file.

```bash
OPENBB_BACKEND=Qt5Agg
```

And run the following commands.

```bash
xhost +local:
docker run -it --rm --name openbb --env-file=./.env -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix ghcr.io/openbb-finance/openbbterminal-poetry:X.Y.Z
xhost -local:
```

If you're using remote docker host, you can connect with "ssh -X <FQDN/IP>".

Then run the previous docker command.
