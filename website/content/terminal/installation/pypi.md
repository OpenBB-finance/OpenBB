---
title: PyPI
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

This section guides you how to install the OpenBB Terminal and SDK from PyPI. This installation type supports Windows, macOS and Linux systems. **Before starting the installation process, make sure the following pieces of software are installed.**

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

Once you have met all of these requirements, you are ready to set up your virtual environment for installation of the OpenBB Terminal and SDK from PyPI.

## Prepare the virtual environment

Download the environment configuration file and the cleanup script from the OpenBB Terminal repository.

On Windows copy and paste these commands into your terminal/command prompt:

```batch
curl -O https://raw.githubusercontent.com/OpenBB-finance/OpenBBTerminal/d19412933245b51643a9e7f2624f1d42907488f4/build/conda/conda-3-9-env.yaml
curl -O https://raw.githubusercontent.com/OpenBB-finance/OpenBBTerminal/d19412933245b51643a9e7f2624f1d42907488f4/build/conda/cleanup_artifacts.bat
```

On macOS and Linux copy and paste these commands into your terminal/command prompt:

```shell
curl -O https://raw.githubusercontent.com/OpenBB-finance/OpenBBTerminal/d19412933245b51643a9e7f2624f1d42907488f4/build/conda/conda-3-9-env.yaml
curl -O https://raw.githubusercontent.com/OpenBB-finance/OpenBBTerminal/d19412933245b51643a9e7f2624f1d42907488f4/build/conda/cleanup_artifacts.sh
```

Create the environment using the following command:

```shell
conda env create -n obb --file conda-3-9-env.yaml
```

Agree to the prompts if there are any.

After the obb environment is created, activate it by entering:

```shell
conda activate obb
```

## Install the OpenBB Terminal and SDK

Make sure you have completed all the previous steps. If you followed the instructions you should have a virtual environment named `obb` and this environment is activated.

Install the main package of Openbb SDK with `pip`, a package manager.

```shell
pip install openbb --no-cache-dir
```

This method provides access to the data aggregation and charting functions of the OpenBB SDK. It does not provide access to the advanced features that are provided by the Portfolio Optimization and Machine Learning toolkits.

The toolkits can be installed individually with:

```shell
pip install openbb[optimization] --no-cache-dir
```

and

```shell
pip install openbb[forecast] --no-cache-dir
```

Install all available toolkits at once with:

```shell
pip install openbb[all] --no-cache-dir
```

## Verify Installation

Once this installation process is completed, you can start the terminal by running:

```shell
openbb
```

To confirm the installation of the SDK, open the Python interpreter with a `python` command, then run the following:

```python
from openbb_terminal.sdk import openbb
openbb.__version__
```

You should see the version number displayed, for example:

```python
'2.5.1'
```

That's it!

**NOTE:** When you are opening the OpenBB Terminal anew, the Python environment will need to be activated again. When using a code editor, make sure that you have the correct environment selected. This should be easy to figure out if you get an error that you are missing packages. To launch the OpenBB Tterminal application in s new terminal window use the following two commands:

```shell
conda activate obb
openbb
```

## Updating the OpenBB SDK Version

You can upgrade the OpenBB SDK to the latest version via `pypi`.

When using the terminal or SDK without toolkits, first activate your environment by running:

```shell
conda activate obb
```
and update the package by running:

```shell
pip install -U openbb --no-cache-dir
```

When using an installation with toolkits, with your virtual environment activated, enter:

```shell
pip install -U openbb[all] --no-cache-dir
```

## Nightly Builds

OpenBB SDK is updated daily with new features and bug fixes, but some features being worked on may be unstable. To use the same SDK version as the development team, install the nightly build with:

```shell
conda activate obb
pip install -U openbb-nightly --no-cache-dir
```

:::info
If you encounter any issues with the installation, please try installing OpenBB Terminal and SDK from source [(link)](/terminal/installation/source).
:::
