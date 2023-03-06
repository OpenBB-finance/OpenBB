---
title: Source
sidebar_position: 4
description: This section guides you a long to install the OpenBB Terminal via Python. This installation type supports both Windows and Unix systems (Linux + MacOS).
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

This section guides you a long to install the OpenBB Terminal via Python. This installation type supports both Windows and Unix systems (Linux + MacOS). **Before starting the installation process, make sure the following pieces of software are installed.**

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

<details><summary>VcXsrv (Windows and Linux only)</summary>

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

Once you have met all of these requirements, you are ready to install the OpenBB Terminal.


## Creating a virtual environment

When a terminal window is opened, if the base Conda environment - look for `(base)` to the left of the cursor on the command line - is not activated automatically, find the path for it by entering:

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

Create the environment by copying the code below into the command line:

```console
conda create -n obb -c conda-forge python=3.10.9 pip pybind11 cmake git cvxpy lightgbm poetry
```

## Activate the obb environment

After the packages from the previous step are installled, activate the newly created environment by entering:

```console
conda activate obb
```

## Install the OpenBB Terminal

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

Once this installation process is completed, you can start the terminal by running:

```bash
python terminal.py
```

**NOTE:** When you are opening the OpenBB Terminal from a Terminal application, the Python environment will need to be activated again - `conda activate obb` - and the current working directory should be the `OpenBBTerminal` folder where the source code was cloned. When using a code editor, make sure that you have the correct environment selected. This should be easy to figure out if you get an error that you are missing packages.

**TROUBLESHOOTING:** Having difficulty getting through the installation, or encountering errors? Check out the [troubleshooting page](/terminal/quickstart/troubleshooting), or reach out to our [Discord](https://discord.gg/Up2QGbMKHY) community for help.

:::info About Poetry

By default we advise using `conda` and `poetry` for environment setup and dependency management. Conda ships binaries for packages like `numpy` so these dependencies are not built from source locally by `pip`. Poetry solves the dependency tree in a way that the dependencies of dependencies of dependencies use versions that are compatible with each other.

For `Conda` environments, the `build/conda` folder contains multiple `.yaml` configuration files to choose from.

When using other python distributions we highly recommend a virtual environment like `virtualenv` or `pyenv` for installing the terminal dependency libraries.

Requirements files that are found in the project root:

- `requirements.txt` list all the dependencies without Machine Learning libraries
- `requirements-full.txt` list all the dependencies with Machine Learning libraries

They can be installed with `pip`:

```bash
pip install -r requirements.txt
```

The dependency tree is solved by poetry.

Note: The libraries specified in the requirements files have been tested and work for the purpose of this project, however, these may be older versions. Hence, it is recommended for the user to set up a virtual python environment prior to installing these. This allows to keep dependencies required by different projects in separate places.

:::