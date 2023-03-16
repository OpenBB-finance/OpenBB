---
title: Installation
sidebar_position: 2
description: The OpenBB SDK provides programmatic access to all Terminal functions. This layer of code allows users to build their own tools and applications on top of the existing architecture. Follow these steps to install on a local machine.
keywords: [installation, installer, install, guide, mac, windows, linux, python, github, macos, how to, explanation, openbb, sdk, api, pip, pypi,]
---
The OpenBB SDK provides programmatic access to all Terminal functions. This layer of code allows users to build their own tools and applications on top of the existing architecture. Follow these steps to install on a local machine. **If the OpenBB Terminal has already been installed in a virtual Python environment, no additional installations are required.**

<details><summary>Minimum Requirements</summary>

- Windows 10, 
- Modern CPU (made in the last 5 years)
- At least 4GB of RAM
- At least 5GB of free storage
- Internet connection (cable or 4G mobile)

</details>

Before continuing with the installation process, make sure the following software is installed:

<details><summary>Miniconda</summary>
Miniconda is a Python environment and package manager. It is required for installing certain dependencies.

Go [here](https://docs.conda.io/en/latest/miniconda.html#latest-miniconda-installer-links) to find the download for your operating system or use the links below:

- Apple-Silicon Systems: [Miniconda for MacOS](https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.pkg)
- Intel-based Mac Systems: [Miniconda for MacOS](https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh)
- Linux and WSL Systems: [Miniconda for Linux](https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh)
- Raspberry PI Systems: [Miniconda for Raspberry PI](https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh)
- Windows Systems: [Miniconda for Windows](https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe)


**NOTE for Apple Silicon Users:** Install Rosetta from the command line: `softwareupdate --install-rosetta`

**NOTE for Windows users:** Install/update Microsoft C++ Build Tools from [here](https://visualstudio.microsoft.com/visual-cpp-build-tools/).
</details>

<details><summary>CMake (Mac and Linux only)</summary>

If you have a **MacBook**, check if homebrew is installed by running `brew --version`

If Homebrew is not installed, run:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install cmake
brew install gcc
```

If Homebrew is already installed:

```bash
brew install cmake
brew install gcc
```

If you have a **Linux** computer, use the following script:

```bash
sudo apt update && sudo apt upgrade
sudo apt install -y gcc cmake
```
</details>

## Create Python Environment

The first step is to create the virtual Python environment. When a terminal window is opened, if the base Conda environment - look for `(base)` to the left of the cursor on the command line - is not activated automatically, find the path for it by entering:

```console
conda env list
```

Copy the path which corresponds with `base`, and activate it with:

```console
conda activate REPLACE_WITH_PATH
```

Check which `conda` version is installed by entering:

```console
conda -V
```

As of writing, the most recent version of `Conda` is, `23.1.0`. If required, update from a lower version with:

```console
conda install -c conda-forge -n base conda=23.1.0
```

Create the environment by copying the code below into the command line:

```console
conda create -n obb -c conda-forge python=3.10.9 pip pybind11 cmake git cvxpy lightgbm poetry
```

## Activate the Environment

After the packages from Step 2 install, activate the newly created environment by entering:

```console
conda activate obb
```

## Install the OpenBB SDK

There are two methods to install the OpenBB SDK. The easiest way is to use PyPi as it requires a single command to be ran. If you would also be looking to make code edits, it can be beneficial to clone the repository.

### Install From PyPi

Inside any terminal run the following:

```bash
pip install "openbb[all]"
```

That's it! The OpenBB SDK can now be imported to any Python session with the line of code below.

```console
from openbb_terminal.sdk import openbb
```

The [OpenBB Terminal](https://docs.openbb.co/terminal) is part of the installation, and the application can be launched from the command line by entering:

```console
openbb
```

### Install via Git Clone

From your code editor or command line, browse to the location the OpenBB Terminal source code should live. Make sure you have completed the previous steps.

This starts by cloning the GitHub repository. This will download the source code to the current working directory.

```console
git clone https://github.com/OpenBB-finance/OpenBBTerminal.git
```

Then, navigate to this folder. This can be done in command line or through the code editor by opening the folder.

```console
cd OpenBBTerminal
```

There are a few packages that required to be installed. This is done through Poetry, a package manager.

```bash
pip install qdldl==0.1.5.post3
poetry install -E all
```

Done! The OpenBB SDK can now be imported to any Python session with the line of code below.

```console
from openbb_terminal.sdk import openbb
```

The Terminal application is also installed, and it can be launched from the command line at the root `OpenBBTerminal` folder with:

```console
python terminal.py
```

## Updating the OpenBB SDK Version

To upgrade the OpenBB SDK to the latest version via `pypi`, with the `obb` Python environment active, enter:

```console
pip install -U openbb[all]
```

To update the OpenBB SDK via the Git Clone method with the `obb` Python environment activated, navigate into the root folder of the cloned project. Then, pull the changes from GitHub:

```console
git fetch
git pull
```

**Note:** If working from a forked repo, the `git pull` command will need to be adjusted to pull from the desired branch, like `origin` or `upstream`. For example, `git pull origin main`; `git pull origin develop`

Update any changes to the dependencies by running:

```console
poetry install -E all
```
