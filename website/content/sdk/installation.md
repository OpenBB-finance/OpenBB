---
title: Installation
sidebar_position: 1
description: The OpenBB SDK provides programmatic access to all Terminal functions. This layer of code allows users to build their own tools and applications on top of the existing architecture. Follow these steps to install on a local machine.
keywords: [installation, installer, install, guide, mac, windows, linux, python, github, macos, how to, explanation, openbb, sdk, api, pip, pypi,]
---
The OpenBB SDK provides programmatic access to all Terminal functions and much more. This layer of code allows users to build their own tools and applications on top of the existing architecture. Follow these steps to install on a local machine.

:::note
If the OpenBB Terminal has already been installed from source code, no additional installation steps are required. **You already have the SDK installed.**
:::

## Minimal Installation

For users who have basic developer tools installed and are using Python through a virtual environment, we recommend the following minimal installation method:

```shell
pip install openbb
```

This method is quick and easy.

If you are not sure or are a little bit technical and need to use the SDK with the Machine Learning and Portfolio Optimization toolkits we recommend following the [Full Installation instructions](#full-installation).

## Full Installation

**Before starting the installation process, make sure the following pieces of software are installed.**

<details><summary>Miniconda</summary>
Miniconda is a Python environment and package manager. It is required for installing certain dependencies.

Go [here](https://docs.conda.io/en/latest/miniconda.html#latest-miniconda-installer-links) to find the download for your operating system or use the links below:

- Apple-Silicon Systems: [Miniconda for MacOS](https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.pkg)
- Intel-based Mac Systems: [Miniconda for MacOS](https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh)
- Linux and WSL Systems: [Miniconda for Linux](https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh)
- Raspberry PI Systems: [Miniconda for Raspberry PI](https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh)
- Windows Systems: [Miniconda for Windows](https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe)

To verify if Miniconda is installed on your system, open the command line and run the following command:

```console
conda --version
```

If Miniconda is installed, you should see the version number displayed, for example:

```console
conda 4.10.3
```

**NOTE for Apple Silicon Users:** Install Rosetta from the command line: `softwareupdate --install-rosetta`

**NOTE for Windows users:** Install/update Microsoft C++ Build Tools from [here](https://visualstudio.microsoft.com/visual-cpp-build-tools/).

</details>

<details><summary>Git</summary>

To check if you have Git installed, open the command line and run the following command:

```console
git --version
```

You should see something like this:

```console
git version 2.31.1
```

If you do not have git installed, install it from `conda` by running:

```console
conda install -c anaconda git
```

Or follow the instructions [here](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) to install it.

</details>

<details><summary>VcXsrv (Windows Subsystem for Linux only)</summary>

Since a WSL installation is headless by default (i.e., there is only access to a terminal running a Linux distribution) there are additional steps required to display visualizations. A more detailed tutorial is found, [here](https://medium.com/@shaoyenyu/make-matplotlib-works-correctly-with-x-server-in-wsl2-9d9928b4e36a).

- Dynamically export the DISPLAY environment variable in WSL2:

```console
# add to the end of ~/.bashrc file
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0
# source the file
source ~/.bashrc
```

- Download and install [VcXsrv](https://sourceforge.net/projects/vcxsrv/)
- When running the program is important to check "Disable access control"

After this, `VcXsrv` should be running successfully, and the machine is ready to proceed with the terminal installation.

Alternatives to `VcXsrv` include:

- [GWSL](https://opticos.github.io/gwsl/)
- [Xming](https://xming.en.softonic.com/)
- [Wayland](https://wayland.freedesktop.org/docs/html/)

</details>

Once you have met all of these requirements, you are ready to install the OpenBB SDK.

## Create and activate the virtual environment

Create the environment by copying the code below into the command line and agreeing to the prompts.

```shell
conda env create -n obb --file https://raw.githubusercontent.com/OpenBB-finance/OpenBBTerminal/main/build/conda/conda-3-9-env.yaml
```

After the obb environment is created, activate it by entering:

```shell
conda activate obb
```

:::note
Apple Silicon users should clean up some artifacts in order for the environment to work nicely with all dependencies. Do this by running:

```shell
find $(dirname $(dirname $(which python)))/lib/python*/site-packages \
     -maxdepth 2 -name direct_url.json \
     -exec rm -f {} +
```

:::

## Install the OpenBB SDK

Install the OpenBB SDK with the Machine Learning and Portfolio Optimization toolkits by running the following command:

```shell
pip install openbb[all]
```

## Verify Installation

Confirm the installation by opening the python interpreter with a `python` command and running the following:

```python
from openbb_terminal.sdk import openbb
openbb.__version__
```

You should see the version number displayed, for example:

```python
'2.5.1'
```

That's it!

:::info
The [OpenBB Terminal](https://docs.openbb.co/terminal) is a part of the SDK installation, and the application can be launched from the command line by entering:

```shell
openbb
```

:::


## Updating the OpenBB SDK Version

You can upgrade the OpenBB SDK to the latest version via `pypi`.

When using a minimal installation, enter:

```shell
pip install -U openbb
```

When using a full installation, with the `obb` Python environment active, enter:

```shell
pip install -U openbb[all]
```
