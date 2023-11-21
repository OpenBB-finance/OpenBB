---
title: Docker
sidebar_position: 5
description: Instructions for installing OpenBB Terminal via Docker on different operating
  systems (Windows, MacOS, Linux). The page includes specific guidelines for Docker
  Desktop installation, displaying charts in Docker, and how to pull and run OpenBB
  Terminal Docker image.
keywords:
- Docker
- Installation
- Windows
- MacOS
- Linux
- VcXsrv
- XQuartz
- docker-compose.yaml
- docker-compose.x11.yaml
- Docker Desktop
- Run OpenBB Terminal Docker image
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Docker - Installation | OpenBB Terminal Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Installing the OpenBB Terminal via Docker supports both Windows and Unix systems (Linux + MacOS). Installation differs a bit between operating system (Windows, macOS and Linux). Please select the section matching to your OS.<p></p>

<Tabs>
<TabItem value="Windows" label="Windows" default>

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

Once downloaded you will open the program and accept all the defaults expect the below settings:
- CHECK the option: `Disable access control` and UNCHECK the `Native opengl` command

**Pull and run the container**

Execute these commands:

```console
curl -o docker-compose.yaml https://raw.githubusercontent.com/OpenBB-finance/OpenBBTerminal/main/build/docker/docker-compose.yaml

docker compose run openbb
```

This will download and run the file: `docker-compose.yaml`

This file contents the settings to pull and run OpenBB Terminal Docker image.
</TabItem>

<TabItem value="MacOS" label="MacOS">

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

Execute these commands:

```console
curl -o docker-compose.yaml https://raw.githubusercontent.com/OpenBB-finance/OpenBBTerminal/main/build/docker/docker-compose.yaml

xhost +$IP
docker compose run -e DISPLAY=$IP:0 openbb
```

This will download and run the file: `docker-compose.yaml`

This file contents the settings to pull and run OpenBB Terminal Docker image.

The `xhost +$IP` and `DISPLAY=$IP:0` parts are there to allow charts display.
</TabItem>
<TabItem value="Linux" label="Linux">

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
 Context:    desktop-linux
 Debug Mode: false

Server:
 Containers: 14
 Running: 2
 Paused: 1
 Stopped: 10
```

**Pull and run the container**

Execute these commands:

```console
curl -o docker-compose.yaml https://raw.githubusercontent.com/OpenBB-finance/OpenBBTerminal/main/build/docker/docker-compose.yaml
curl -o docker-compose.x11.yaml https://raw.githubusercontent.com/OpenBB-finance/OpenBBTerminal/main/build/docker/docker-compose.x11.yaml

docker compose -f docker-compose.yaml -f docker-compose.x11.yaml run openbb
```

:::note
If you are experiencing issues with charts - launch the container with the following command:

```console
docker compose -f docker-compose.yaml -f docker-compose.x11.yaml run -e WEBKIT_DISABLE_COMPOSITING_MODE=1 openbb
```

:::

:::note
If you're using remote docker host, you can connect with `ssh -X <FQDN/IP>`.
:::

</TabItem>
</Tabs>
