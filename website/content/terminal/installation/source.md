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

<!-- markdownlint-disable MD012 MD031 MD033 -->

This section guides you how to install the OpenBB Terminal from source code. This installation type supports Windows, macOS and Linux systems. **Before starting the installation process, make sure the following pieces of software are installed.**

<details><summary>Miniconda</summary>
Miniconda is a Python environment and package manager. It is required for installing certain dependencies.

Go [here](https://docs.conda.io/en/latest/miniconda.html#latest-miniconda-installer-links) to find the download for your operating system or use the links below:

- Apple-Silicon Systems: [Miniconda for MacOS](https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.pkg)
- Intel-based Mac Systems: [Miniconda for MacOS](https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh)
- Linux and WSL Systems: [Miniconda for Linux](https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh)
- Raspberry PI Systems: [Miniconda for Raspberry PI](https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh)
- Windows Systems: [Miniconda for Windows](https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe)

To verify if Miniconda is installed on your system, open the command line and run the following command:

```shell
conda --version
```

If Miniconda is installed, you should see the version number displayed, for example:

```shell
conda 23.1.0
```

**NOTE for Apple Silicon Users:** Install Rosetta from the command line: `softwareupdate --install-rosetta`

**NOTE for Windows users:** Install/update Microsoft C++ Build Tools from [here](https://visualstudio.microsoft.com/visual-cpp-build-tools/).

</details>

<details><summary>Git</summary>

To check if you have Git installed, open the command line and run the following command:

```shell
git --version
```

You should see something like this:

```shell
git version 2.31.1
```

If you do not have git installed, install it from `conda` by running:

```shell
conda install -c anaconda git
```

Or follow the instructions [here](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) to install it.

</details>

<details><summary>VcXsrv (Windows Subsystem for Linux only)</summary>

Since a WSL installation is headless by default (i.e., there is only access to a terminal running a Linux distribution) there are additional steps required to display visualizations. A more detailed tutorial is found, [here](https://medium.com/@shaoyenyu/make-matplotlib-works-correctly-with-x-server-in-wsl2-9d9928b4e36a).

- Dynamically export the DISPLAY environment variable in WSL2:

```shell
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

<details><summary>GTK toolchains (Linux only)</summary>

GTK is a window extension that is used to display interactive charts and tables. The library responsible for interactive charts and tables (`pywry`) requires that you install certain dependencies based on the Linux distribution that you are using.

<details>
<summary>Debian-based / Ubuntu / Mint</summary>

```shell
sudo apt install libwebkit2gtk-4.0-dev
```

</details>

<details>
<summary>Arch Linux / Manjaro</summary>

```shell
sudo pacman -S webkit2gtk-4.0
```

</details>

<details>
<summary>Fedora</summary>

```shell
sudo dnf install gtk3-devel webkit2gtk4.0-devel
```

</details>

</details>

Once you have met all of these requirements, you are ready to install the OpenBB Terminal from source.

## Clone the source code

Clone the OpenBB Terminal source code from GitHub. This will download the source code to the current working directory.

```console
git clone https://github.com/OpenBB-finance/OpenBBTerminal.git
```

Enter the directory:

```console
cd OpenBBTerminal
```

## Create and activate the virtual environment

Create the environment by copying the code below into the command line and agreeing to the prompts.

```shell
conda env create -n obb --file build/conda/conda-3-10-env.yaml
```

After the obb environment is created, activate it by entering:

```shell
conda activate obb
```

:::note
After you activate the new environment for the first time it is required to clean up some artifacts in order for all dependencies to work nicely.

On macOS and Linux do this by running this script (copy and paste the launch code):

```shell
build/conda/cleanup_artifacts.sh
```

On Windows do this by running this script (copy and paste the launch code):

```shell
build/conda/cleanup_artifacts.bat
```

:::

## Install the OpenBB Terminal

Make sure you have completed all the previous steps. If you followed the instructions you should be in the location where the OpenBB Terminal source code lives.

Install the remaining dependencies and the terminal through Poetry, a package manager.

```shell
poetry install -E all
```
:::info
<details><summary>Read about Conda, Poetry and Python package management</summary>

For the best user experience we advise using `conda` and `poetry` for environment setup and dependency management. Conda ships binaries for packages like `numpy` so these dependencies are not built from source locally by `pip`. Poetry solves the dependency tree in a way that the dependencies of dependencies of dependencies use versions that are compatible with each other.

For `Conda` environments, the `build/conda` folder contains multiple `.yaml` configuration files to choose from.

When using other python distributions we highly recommend a virtual environment like `virtualenv` or `pyenv` for installing the terminal dependency libraries.

For people who prefer using "vanilla" `pip` the requirements files are found in the project root:

- `requirements.txt` list main dependencies
- `requirements-full.txt` list all the dependencies including Machine Learning and Portfolio Optimization libraries and dependencies for developers

They can be installed with `pip`:

```shell
pip install -r requirements.txt
```

The dependency tree is solved by poetry.

Note: The libraries specified in the requirements files have been tested and work for the purpose of this project, however, these may be older versions. Hence, it is recommended for the user to set up a python virtual environment prior to installing these. This allows to keep dependencies required by different projects in separate places.

After installing the requirements you can install the terminal with:

```shell
pip install .
```

</details>
:::

Once this installation process is completed, you can start the terminal by running:

```shell
openbb
```

**NOTE:** When you are opening the OpenBB Terminal anew, the Python environment will need to be activated again. When using a code editor, make sure that you have the correct environment selected. This should be easy to figure out if you get an error that you are missing packages. To launch the OpenBB Tterminal application in s new terminal window use the following two commands:

```shell
conda activate obb
openbb
```

**TROUBLESHOOTING:** Having difficulty getting through the installation, or encountering errors? Reach out to our [Discord](https://discord.gg/Up2QGbMKHY) community for help.
