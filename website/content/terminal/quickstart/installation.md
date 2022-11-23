---
sidebar_position: 1
title: Installation
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

The OpenBB Terminal can be directly installed on your computer via our installation program. Within this section, you are guided through the installation process and how to launch the program. If you struggle with the installation process, please don’t hesitate to reach us on [Discord](https://openbb.co/discord) or visit our [contact page](https://openbb.co/contact).

OpenBB Terminal is available in all major platforms. With MacOS/Windows you can easily install with the installer (instructions below). It is also available to install on Linux with Docker or from source.

:::info Installation Instructions

<Tabs>
  <TabItem value="Windows" label="Windows">Install on Windows
  <div class="gdoc-page">

</div><p>The process starts off by downloading the installer, see below for how to download the most recent release:</p>
<ol>
<li>Go to the <a href="https://www.openbb.co/products/terminal#get-started" target="_blank">OpenBB website</a>.</li>
<li>Click on the <code>Download</code> button in the Windows Installer section.</li>
</ol>
<p>When the file is downloaded, use the following steps to run the OpenBB Terminal:</p>
<div class="gdoc-columns">

<div class="gdoc-columns__content gdoc-markdown--nested">
    <p><strong>Step 1: Double-click the <code>.exe</code> file that got downloaded to your <code>Downloads</code> folder</strong></p>
<p>You will most likely receive the error below stating &ldquo;Windows protected your PC&rdquo;. This is because the installer is
still in beta phase, and the team has not yet requested verification from Windows.</p>
<p align="center"><a target="_blank" href="https://user-images.githubusercontent.com/46355364/169502271-69ad8075-165f-4b1a-8ab8-254d643a5dae.png"><img width="500" alt="windows_protected_your_pc" src="https://user-images.githubusercontent.com/46355364/169502271-69ad8075-165f-4b1a-8ab8-254d643a5dae.png"></img></a></p>

</div>

<div class="gdoc-columns__content gdoc-markdown--nested">
    <p><strong>Step 2: Click on <code>More info</code> and select <code>Run anyway</code> to start the installation process</strong></p>
<p>Proceed by following the steps. Do note that if you wish to install the application to &ldquo;Program Files&rdquo; that you will have to run the resulting application as Administrator.</p>
<p align="center"><a target="_blank" href="https://user-images.githubusercontent.com/46355364/169502143-ba88de53-7757-48f2-9ec4-748d4917044b.png"><img width="500" alt="run_anyway" src="https://user-images.githubusercontent.com/46355364/169502143-ba88de53-7757-48f2-9ec4-748d4917044b.png"></img></a></p>

</div>

<div class="gdoc-columns__content gdoc-markdown--nested">
    <p><strong>Step 3: Double-click on the application that appeared on your Desktop, you are now able to run the OpenBB Terminal</strong></p>
<p>The first time this takes a bit longer to load, this can take up to a few minutes.</p>
<p align="center"><a target="_blank" href="https://user-images.githubusercontent.com/46355364/169502187-f4e42333-a947-464b-9320-a8f63c7ce089.png"><img width="500" alt="run_the_terminal" src="https://user-images.githubusercontent.com/46355364/169502187-f4e42333-a947-464b-9320-a8f63c7ce089.png"></img></a></p>

</div>

</div>
</TabItem>

<TabItem value="macOS" label="MacOS">Install on macOS 🍎

<div class="gdoc-page">
</div><p>The process starts off by downloading the installer, see below for how to download the most recent release:</p>
<ol>
<li>Go to the <a href="https://www.openbb.co/products/terminal#get-started" target="_blank">OpenBB website</a>.</li>
<li>Click on the <code>Download</code> button in the macOS Installer section.</li>
</ol>
<p>When the DMG file is downloaded, use the following steps to run the OpenBB Terminal:</p>
<div class="gdoc-columns">

<div class="gdoc-columns__content gdoc-markdown--nested">
    <p><strong>Step 1: Open the downloaded <code>OpenBB Terminal.dmg</code> and copy <code>OpenBB Terminal</code> folder into your <code>Applications</code></strong></p>
<p>Open the <code>OpenBB Terminal.dmg</code> file that got saved to your &ldquo;Downloads&rdquo; folder and drag the &ldquo;OpenBB Terminal&rdquo; folder into &ldquo;Applications&rdquo; folder. A link to the <code>Applications</code> folder is presented on the screen.
Note that this should take some time as it is extracting the files from the .dmg file.</p>
<p align="center"><img width="100%" alt="image" src="https://user-images.githubusercontent.com/11668535/173027899-9b25ae4f-1eef-462c-9dc9-86086e9cf197.png"></img></p>

</div>

<div class="gdoc-columns__content gdoc-markdown--nested">
    <p><strong>Step 2: Open the <code>OpenBB Terminal</code> app in the folder that you have just copied to your <code>Applications</code>.</strong></p>
<p>During first launch if you get a message saying that the application can&rsquo;t be launched, do the following:
Right-Click the app and select <code>Open</code>. You will see a message saying that macOS was not able to check whether the application contains malicious software. Click <code>Open</code> to proceed.</p>
<p align="center"><img width="100%" alt="image" src="https://user-images.githubusercontent.com/11668535/173027798-b4d25a20-d932-4ed9-a8ce-f911c4ee4342.png"></img></p>

</div>

</div>
</TabItem>
  <TabItem value="docker" label="Docker">Install with Docker
  Here are the steps to get OpenBBTerminal using the Docker containers that we provide:

Installing Docker and Docker Compose Pulling and running OpenBBTerminal Docker
Container Configuring your X-server to show plots Each of this steps need to be
followed to have a working version of OpenBBTerminal.

We will detail these steps in the rest of this document.

### 1. Installing Docker and Docker Compose

INSTALL DOCKER

Installing Docker Desktop is the easiest way for most people:

It has a Graphical User Interface and comes with Docke Compose in it.

You can find Docker Desktop installation file for your OS here:

Download Docker Desktop

START DOCKER

Once you have Docker installed and running, you can use the following command to
check the state:

docker info It should output a text like this one:

Client: Context: default Debug Mode: false

Server: Containers: 14 Running: 2 Paused: 1 Stopped: 10 ... If you see a message
like the following, it most likely means you need to start Docker.

Open the docker desktop app in this case.

Server: ERROR: Cannot connect to the Docker daemon at
unix:///var/run/docker.sock. Is the docker daemon running?

### 2. Pulling and running OpenBBTerminal Docker Container

DOCKER COMPOSE

Here are the commands to use Docker Compose to pull and run the OpenBBTerminal
Docker Container:

```bash
curl -o docker-compose.yaml https://raw.githubusercontent.com/OpenBB-finance/OpenBBTerminal/main/docker/docker-compose.yaml
docker compose run poetry
```

The command line with curl is downloading this file : docker-compose.yaml.

The docker-compose.yaml file is a configuration file telling Docker Compose:

where to find OpenBBTerminal Docker Container how to run this container. The
second command runs Docker Compose on the service poetry defined in this
docker-compose.yaml file.

This second command must be run in the same folder in which docker-compose.yaml
file is.

DOCKER

If you don't have Docker Compose you can also use Docker directly to run the
OpenBBTerminal Docker Container.

Here is the commands to run:

```bash
docker pull ghcr.io/openbb-finance/openbbterminal-poetry:X.Y.Z

docker run -v ~/.openbb_terminal/:/home/python/.openbb_terminal -v ~/OpenBBUserData:/home/python/OpenBBUserData -it --rm ghcr.io/openbb-finance/openbbterminal-poetry:X.Y.Z
```

Be sure to replace X.Y.Z with the version you want to pull and run.

Note for windows:

    Ignore this message if you are using Powershell or a more evolved interpreters.
    If you are using the builtin Windows interpreter.
    Replace `~` by `%USERPROFILE%` in the command above.

### 3. Configuring your X-server to show plots

In order to display plots in the docker container, we need to configure the
XServer on the host machine. Without this configuration the interactive charts
will not be displayed.

On Windows Download and install : VcXsrv

When running the program is important to check "Disable access control"

Run Docker Compose like this:

```bash
curl -o docker-compose.yaml https://raw.githubusercontent.com/OpenBB-finance/OpenBBTerminal/main/docker/docker-compose.yaml
docker compose run poetry
```

Or run Docker directly:

```bash
docker run -v ~/.openbb_terminal:/home/python/.openbb_terminal -v ~/OpenBBUserData:/home/python/OpenBBUserData -it --rm --env DISPLAY=host.docker.internal:0.0 ghcr.io/openbb-finance/openbbterminal-poetry:X.Y.Z
```

X-Server on macOS Users familiar with Docker and X-Server can set the DISPLAY
variable in the file setenv described above. If you use this approach remember
to add :0 at the end of your inet address. E.g. DISPLAY=192.168.1.155:0.

For help setting up the X-Server continue reading:

Setting up X Quartz/X11 On macOS the X11 client of choice is XQuartz. On Windows
it's Xming. XQuartz will be used as an example further on.

Install X Quartz from https://www.xquartz.org/ With X Quartz open: go to
Preferences -> Security and make sure both options are enabled.
<img width="60%" alt="image" src="https://user-images.githubusercontent.com/18151143/132548605-235d774b-9aa6-4a45-afcf-58fb775d376a.png"></img>
Adding the display for Docker From the command prompt or terminal, run the
following to add your local configuration to the list of allowed access control:

```bash
IP=$(ifconfig | grep inet | grep -v -e "127.0.0.1" | awk '$1=="inet" {print $2}')
xhost + $IP
```

Now we can run the docker container, adding the display to the environment:

```bash
docker run -v ~/.openbb_terminal/:/home/python/.openbb_terminal -v ~/OpenBBUserData:/home/python/OpenBBUserData -it --rm --env-file=path/to/setenv --env DISPLAY=$IP:0 ghcr.io/openbb-finance/openbbterminal-poetry:X.Y.Z
```

This container will be able to display all the same plots as the terminal
interface.

X-Server on Linux Desktop X-Server is default in Linux distribution. There is no
need to install any clients.

Local docker container We can use IPC socket to connect Desktop.

Add this setting to your .env file.

```bash
OPENBB_BACKEND=Qt5Agg
```

And run the following commands.

```bash
xhost +local:
docker run -it --rm --name openbb --env-file=./.env -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix ghcr.io/openbb-finance/openbbterminal-poetry:X.Y.Z
xhost -local:
```

If you're using remote docker host, you can connect with `ssh -X <FQDN/IP>`.

Then run the previous docker command.

</TabItem>
  <TabItem value="Source" label="Source">
This installation type supports both Windows and Unix systems (Linux + MacOS).

**NOTE for Windows users:** Some _not all_ Windows users would prefer to use an environment
similar to what Linux and macOS users use. In this case it is easier to use Windows Subsystem
for Linux (WSL). WSL emulates a Linux machine inside your Windows system. If this is the case -
jump to the <a href="#installing-wsl-only-for-windows-users">Installing WSL (Only for Windows users)</a>
section before proceeding.

### Installing the terminal

These steps are common in all operating systems (Windows with or without WSL, MacOS or Linux).

This project supports Python 3.8 and 3.9. By default, the newly created virtual environment will use Python 3.9.13

Our current recommendation is to use this project with Anaconda's Python distribution - either full
[**Anaconda3 Latest**](https://www.anaconda.com/products/distribution) or
[**Miniconda3 Latest**](https://docs.conda.io/en/latest/miniconda.html) (recommended).
Several features in this project utilize Machine Learning. Machine Learning Python dependencies are optional. For MacOS systems, the "Miniconda3 MacOSX 64-bit" version that works on both Intel and M1
macs is recommended.

**NOTE:** We recommend using `conda` and `poetry` because it just works. You can use other python
distributions and use raw `pip` instead of `poetry` but you will very likely bump into installation
issues.

#### 1. [Install Miniconda](https://docs.conda.io/en/latest/miniconda.html)

Miniconda is a python environment and package manager. It is required if you want to
have the dependencies working straight away.

- Follow the [link to the page with the latest installers for all platforms](https://docs.conda.io/en/latest/miniconda.html#latest-miniconda-installer-links) or click direct links to installer packages based on your operating system:
  - If you are using macOS click [Miniconda for MacOS](https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh)
  - If you are using WSL or Linux click [Miniconda for Linux](https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh)
  - If you are using a Raspberry PI click [Miniconda for Raspberry PI](https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh)
  - If you are using Windows click [Miniconda for Windows](https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe).

      **ONLY REQUIRED ON WINDOWS IF NOT USING WSL**, Install/update Microsoft C++ Build Tools from here: <https://visualstudio.microsoft.com/visual-cpp-build-tools/>

   **NOTE for macOS users:** The link above gets you the Intel version of miniconda meaning if you're on an
   Apple Silicon powered machine you will be using the terminal through Apple's rosetta2 layer. We recommend
   sticking to this distribution for better compatibility until the dependency developers fully catch up with
   Apple's transition to Apple Silicon.

- After following the steps, confirm that you have it by opening a terminal and running: `conda -V`. The output should be something along the lines of: `conda 22.9.0`

#### 2. Install CMake

CMake is required by several python modules.

**On Linux or Raspberry Pi:**

```bash
sudo apt update
sudo apt install -y gcc cmake
```

**On macOS:**

Check if you have homebrew installed by running `brew --version`

If you don't have homebrew installed run:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install cmake
```

If you have homebrew installed run:

```bash
brew install cmake
```

**On Windows:**

If you have followed the instructions in step 1 of this guide CMake was installed as a
part of you Microsoft C++ Build Tools

#### 3. Install git

```bash
conda install -c anaconda git
```

#### 4. Clone the Project

- Via HTTPS: `git clone https://github.com/OpenBB-finance/OpenBBTerminal.git`
- via SSH: `git clone git@github.com:OpenBB-finance/OpenBBTerminal.git`

#### 5. Navigate into the project's folder

```bash
cd OpenBBTerminal/
```

#### 6. Create Environment

You can name the environment whatever you want. Although you could use names such as:
`welikethestock`, `thisistheway` or `diamondhands`, we recommend something simple and
intuitive like `obb`. This is because this name will be used from now onwards.

Please note, the following setup has been confirmed to work for all OS (including M1)
with the standard miniconda distribution. If you are using a different distribution,
you will need to install it manually before proceeding.

```bash
conda env create -n obb --file build/conda/conda-3-9-env.yaml
```

Or, to include machine learning type:

```bash
conda env create -n obb --file build/conda/conda-3-9-env-full.yaml
```

Note: Using python 3.10+ can lead to undesirable functionality for certain commands.

#### 7. Activate the virtual environment

```bash
conda activate obb
```

Note: At the end, you can deactivate it with: `conda deactivate`.

#### 8. Install dependencies with poetry

Install the main dependencies with

```bash
poetry install
```

You are good to go with the core of the OpenBB Terminal. To install additional toolkits
proceed with the following commands:

To install the Portfolio Optimization Toolkit run:

```bash
poetry install -E optimization
```

To install the Machine Learning Toolkit run:

```bash
poetry install -E prediction
```

To install both the Portfolio Optimization and the Machine Learning Toolkit run:

```bash
poetry install -E all
```

#### 9. You're ready to use the terminal!

```bash
openbb
```

Or if you are old-fashioned run:

```bash
python terminal.py
```

**NOTE:** When you close the terminal and re-open it, the only command you need to re-call
is `conda activate obb` before you call `openbb` again.

**TROUBLESHOOT:** If you are having troubles to install, check out the
[troubleshoot page](https://github.com/OpenBB-finance/OpenBBTerminal/blob/master/TROUBLESHOOT.md).

You can also reach for help on our [discord](https://discord.gg/Up2QGbMKHY).

## Advanced User Install - Custom installation procedures

By default we advice using `conda` and `poetry` for environment setup and dependency management.
Conda ships binaries for packages like `numpy` so these dependencies are not built from source locally by `pip`.
Poetry solves the dependency tree in a way that the dependencies of dependencies of dependencies
use versions that are compatible with each other.

If you are using a conda environment the `build/conda` folder contains multiple `.yaml` configuration
files that you can choose from.

If you are using other python distributions we highly recommend that you use some virtual
environment like `virtualenv` or `pyenv` for installing the terminal dependency libraries.

Requirements files that you can find in the project root:

- `requirements.txt` list all the dependencies without Machine Learning libraries
- `requirements-full.txt` list all the dependencies without Machine Learning libraries

You can install them with with pip

 ```bash
 pip install -r requirements.txt
 ```

The dependency tree is solved by poetry.

Note: The libraries specified in the requirements files have been tested and work for
the purpose of this project, however, these may be older versions. Hence, it is recommended
for the user to set up a virtual python environment prior to installing these. This allows
to keep dependencies required by different projects in separate places.

### Installing WSL (Only for Windows users)

If you are using Windows you first you need to install WSL. The process is simple and a tutorial can be found [here](https://www.sitepoint.com/wsl2/).
Once you reach the section **Update Linux** on that tutorial, you should have a linux machine installed and can proceed
to the next steps.

Since WSL installation is headless by default (i.e., you have only access to a terminal running a linux distribution)
you need some extra steps to be able to visualize the charts produced by the terminal (more detailed tutorial [here](https://medium.com/@shaoyenyu/make-matplotlib-works-correctly-with-x-server-in-wsl2-9d9928b4e36a)):

1. Dynamically export the DISPLAY environment variable in WSL2:

   ```bash
   # add to the end of ~/.bashrc file
   export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0
   # source the file
   source ~/.bashrc
   ```

2. Download and install [VcXsrv](https://sourceforge.net/projects/vcxsrv/)
3. When running the program is important to check "Disable access control"

After this, `VcXsrv` should be running successfully and we can proceed to terminal installation.

## Update Terminal

The terminal is constantly being updated with new features and bug fixes, hence, for your terminal to be update,
you can run:

```bash
git pull
```

to get the latest changes.

If this fails due to the fact that you had modified some python files, and there's a conflict with the updates, you can use:

```bash
git stash
```

Then, re-run `poetry install` to get any new dependencies.

Once installation is finished, you're ready to openbb.

If you `stashed` your changes previously, you can un-stash them with:

```bash
git stash pop
```

**NOTE:** When you close the terminal and re-open it, the only command you need to re-call is `conda activate gst`
before you call `openbb` again.
</TabItem>
</Tabs>

:::
