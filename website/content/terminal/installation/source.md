---
title: Source
sidebar_position: 3
description: Comprehensive guide to install the OpenBB Terminal and SDK from source.
  The guide covers the installation process for Windows, macOS, and Linux systems
  and covers various software installations including Miniconda, Git, Microsoft C++
  Build Tools, Rosetta2, LibOMP, VcXsrv, and GTK toolchains. Instructions for environment
  setup and package management through Conda and Poetry are also included, along with
  troubleshooting tips and community support.
keywords:
- Installation
- Miniconda
- Git
- Microsoft C++ Build Tools
- Rosetta2
- LibOMP
- VcXsrv
- GTK toolchains
- Conda
- Poetry
- Environment setup
- Python package management
- Troubleshooting
- Community support
- Linux
- MacOS
- Windows
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Source - Installation | OpenBB Terminal Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

This section provides steps to install the OpenBB Terminal and SDK from source. This installation type supports Windows, macOS and Linux systems. **Before starting the installation process, make sure the following pieces of software are installed.**

<details><summary>Miniconda</summary>
Miniconda is a Python environment and package manager. It is required for installing certain dependencies.

Go [here](https://docs.conda.io/en/latest/miniconda.html#latest-miniconda-installer-links) to find the download for your operating system or use the links below:

- Apple-Silicon Systems: [Miniconda for MacOS](https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.pkg)
- Intel-based Mac Systems: [Miniconda for MacOS](https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh)
- Linux and WSL Systems: [Miniconda for Linux](https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh)
- Raspberry PI Systems: [Miniconda for Raspberry PI](https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh)
- Windows Systems: [Miniconda for Windows](https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe)

To verify if Miniconda is installed on the system, open the command line and run the following command:

```shell
conda --version
```

If Miniconda is installed, a version number will be displayed, for example:

```shell
conda 23.1.0
```

There is a good chance the version of Conda is not current. Update it with the command below:

```shell
conda update -n base -c conda-forge conda
```

</details>

<details><summary>Git</summary>

Check to verify if Git is installed by running the following command:

```shell
git --version
```

Which will print something like this:

```shell
git version 2.31.1
```

If Git is not installed, install it now from `conda` by running:

```shell
conda install git
```

Or follow the instructions [here](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) to install it.

</details>

<details><summary>Microsoft C++ Build Tools (Windows only)</summary>

Use the instructions [here](https://visualstudio.microsoft.com/visual-cpp-build-tools/) to install or update Microsoft C++ Build Tools.

![image](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/ceb57be0-6dae-42f2-aca6-bf62ce7d6135)

![image](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/f8aef8fc-a080-4164-bd36-460714ec44f3)


</details>

<details><summary>Rosetta2 (Apple Silicon only)</summary>

Install Rosetta from the terminal with:
```shell
softwareupdate --install-rosetta
```

</details>

<details><summary>LibOMP (Apple Silicon only)</summary>

Apple Silicon does not ship `libomp` by default. It will need to be installed manually for some features of the ML toolkit to work. The `libomp` library can be installed from [homebrew](https://brew.sh/).

Check if Homebrew is installed by running the following command:

```shell
brew --version
```

If Homebrew is not installed, install it by running:

```shell
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Or follow the instructions [here](https://brew.sh/).

To install LibOMP, run the following command:

```shell
brew install libomp
```

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

GTK is a window extension that is used to display interactive charts and tables. The library responsible for interactive charts and tables (`pywry`) requires certain dependencies, based on the Linux distribution, to be installed first.

<details>
<summary>Debian-based / Ubuntu / Mint</summary>

```shell
sudo apt install libwebkit2gtk-4.0-dev
```

</details>

<details>
<summary>Arch Linux / Manjaro</summary>

```shell
sudo pacman -S webkit2gtk
```

</details>

<details>
<summary>Fedora</summary>

```shell
sudo dnf install gtk3-devel webkit2gtk3-devel
```

</details>

</details>

Proceed to next steps once the requirements above have been met.

## Clone the Source Code

Clone the OpenBB Terminal source code from GitHub. This will download the source code to the current working directory.

```console
git clone https://github.com/OpenBB-finance/OpenBBTerminal.git
```

Enter the directory:

```console
cd OpenBBTerminal
```

## Create and Activate the Virtual Environment

Create the environment by copying the code below into the command line and agreeing to the prompts.

```shell
conda env create -n obb --file build/conda/conda-3-9-env.yaml
```

:::note
Additional `YAML` files provide support for Python versions 3.8 and 3.10.  Substitute the `9`, in the command above, with the desired version.
:::

After the obb environment is created, activate it by entering:

```shell
conda activate obb
```

:::note
When the new environment is activated for the first time, it is required to clean up some artifacts in order for all dependencies to work nicely.

On macOS and Linux do this by running this script (copy and paste the launch code):

```shell
build/conda/cleanup_artifacts.sh
```

On Windows do this by running this script (copy and paste the launch code):

```shell
build\conda\cleanup_artifacts.bat
```

:::

## Install the OpenBB Terminal

Make sure to have completed all previous steps. If followed, the current working directory will be the location where the OpenBB Terminal source code lives.

Install the remaining dependencies and the terminal through Poetry, a package manager.

```shell
poetry install -E all
```
:::info
<details><summary>Read about Conda, Poetry and Python package management</summary>

For the best user experience we advise using `conda` and `poetry` for environment setup and dependency management. Conda ships binaries for packages like `numpy` so these dependencies are not built from source locally by `pip`. Poetry solves the dependency tree in a way that the dependencies of dependencies of dependencies use versions that are compatible with each other.

For `Conda` environments, the `build/conda` folder contains multiple `.yaml` configuration files to choose from.

When using other Python distributions we highly recommend a virtual environment like `virtualenv` or `pyenv` for installing the terminal dependency libraries.

For people who prefer using "vanilla" `pip` the requirements files are found in the project root:

- `requirements.txt` list main dependencies
- `requirements-full.txt` list all the dependencies including Machine Learning and Portfolio Optimization libraries and dependencies for developers

They can be installed with `pip`:

```shell
pip install -r requirements.txt
```

The dependency tree is solved by poetry.

Note: The libraries specified in the requirements files have been tested and work for the purpose of this project, however, these may be older versions. Hence, it is recommended for the user to set up a Python virtual environment prior to installing them. This keeps dependencies required by different projects in separate places.

After installing the requirements, install the terminal with:

```shell
pip install .
```

</details>
:::

Once this installation process is completed, start the terminal by running:

```shell
python terminal.py
```

**NOTE:** When the OpenBB Terminal is opened next, the Python environment will need to be activated again. When using a code editor, make sure that the correct environment is selected. This should be easy to figure out if there is an error stating that there are missing packages. To launch the OpenBB Terminal application in a new terminal window, first navigate into the folder where the source code was cloned, and then use the following two commands:

```shell
conda activate obb
python terminal.py
```

**TROUBLESHOOTING:** Having difficulty getting through the installation, or encountering errors? Reach out to our [Discord](https://discord.gg/Up2QGbMKHY) community for help.
