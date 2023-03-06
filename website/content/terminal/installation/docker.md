---
title: Docker
sidebar_position: 3
description: Installing the OpenBB Terminal via Docker supports both Windows and Unix systems (Linux + MacOS). Installation differs a bit between operating system (Windows, macOS and Linux). Please select the section matching to your OS.
keywords:
  [
    installation,
    installer,
    install,
    guide,
    mac,
    windows,
    linux,
    python,
    github,
    macos,
    how to,
    explanation,
    openbb terminal,
  ]
---

Installing the OpenBB Terminal via Docker supports both Windows and Unix systems (Linux + MacOS). Installation differs a bit between operating system (Windows, macOS and Linux). Please select the section matching to your OS.<p></p>

<details><summary>Windows</summary>

**Install Docker Desktop**

You can find `Docker Desktop` for Windows here: [Download Docker Desktop](https://www.docker.com/products/docker-desktop)

**Start Docker**

Execute the following command:

```console
docker info
```

If you have something like this, it means you haven't started Docker:

```console
docker info
Server:
ERROR: Cannot connect to the Docker daemon at unix:///var/run/docker.sock.
Is the docker daemon running?
```

Start Docker, this is how the right output looks like:

```console
docker info
Client:
Context:    default
Debug Mode: false

Server:
Containers: 14
Running: 2
Paused: 1
Stopped: 10
```

**Install VcXsrv**

To display charts with your container, you need: VcXsrv.

You can download VcXsrv here: [Download VcXsrv](https://sourceforge.net/projects/vcxsrv)

When running VcXsrv program check the option: `Disable access control`

**Pull and run the container**

Execute this commands:

```console
curl -o docker-compose.yaml https://raw.githubusercontent.com/OpenBB-finance/OpenBBTerminal/main/build/docker/docker-compose.yaml

docker compose run openbb
```

This will download and run the file: `docker-compose.yaml`

This file contents the settings to pull and run OpenBB Terminal Docker image.
</details>

<details><summary>MacOS</summary>

**Install Docker Desktop**

You can find `Docker Desktop` for MacOS here: [Download Docker Desktop](https://www.docker.com/products/docker-desktop)

**Start Docker**

Execute the following command:

```console
docker info
```

If you have something like this, it means you haven't started Docker:

```console
docker info
Server:
ERROR: Cannot connect to the Docker daemon at unix:///var/run/docker.sock.
Is the docker daemon running?
```

Start Docker, this is how the right output looks like:

```console
docker info
Client:
Context:    default
Debug Mode: false

Server:
Containers: 14
Running: 2
Paused: 1
Stopped: 10
```

**Install XQuartz**

You can download XQuartz here: [Download XQuartz](https://www.xquartz.org)

Open X Quartz.

Then on `Preferences > Security`.

Make sure both of these options are enabled:

- `Authenticate connections`
- `Allow connections from network clients`

It should look like this:
![Screen Shot 2021-09-08 at 12 21 48 PM](https://user-images.githubusercontent.com/18151143/132548605-235d774b-9aa6-4a45-afcf-58fb775d376a.png)

**Get Docker IP**

To get Docker IP you can use this command:

```bash
IP=$(ifconfig | grep inet | grep -v "127.0.0.1" | awk '$1=="inet" {print $2}')
```

**Pull and run the container**

Execute this commands:

```console
curl -o docker-compose.yaml https://raw.githubusercontent.com/OpenBB-finance/OpenBBTerminal/main/build/docker/docker-compose.yaml

xhost +$IP
docker compose run -e DISPLAY=$IP:0 openbb
```

This will download and run the file: `docker-compose.yaml`

This file contents the settings to pull and run OpenBB Terminal Docker image.

The `xhost +$IP` and `DISPLAY=$IP:0` parts are there to allow charts display.


</details>

<details><summary>Linux</summary>

**Install Docker Desktop**

You can find `Docker Desktop` for Linux here: [Download Docker Desktop](https://www.docker.com/products/docker-desktop)

**Start Docker**

Execute the following command:

```console
docker info
```

If you have something like this, it means you haven't started Docker:

```console
docker info
Server:
ERROR: Cannot connect to the Docker daemon at unix:///var/run/docker.sock.
Is the docker daemon running?
```

Start Docker, this is how the right output looks like:

```console
docker info
Client:
Context:    default
Debug Mode: false

Server:
Containers: 14
Running: 2
Paused: 1
Stopped: 10
```

**Pull and run the container**

Execute this commands:

```console
curl -o docker-compose.yaml https://raw.githubusercontent.com/OpenBB-finance/OpenBBTerminal/main/build/docker/docker-compose.yaml

xhost +local:
docker compose run openbb
```

Note: if you're using remote docker host, you can connect with `ssh -X <FQDN/IP>`.

</details>
