---
title: PyPI
sidebar_position: 4
description: This section provides steps to install the OpenBB Terminal from PyPI. This installation type supports Windows, macOS and Linux systems.
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
    pypi,
    miniconda,
    git,
    c++,
    rosetta2,
    libomp,
    vcxsrv,
    gtk
  ]
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="PyPI - Terminal | OpenBB Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

This section provides steps to install the OpenBB Terminal and SDK from PyPI. This installation type supports Windows, macOS and Linux systems. **Before starting the installation process, make sure the following pieces of software are installed.**

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
conda install -c anaconda git
```

Or follow the instructions [here](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) to install it.

</details>

<details><summary>Microsoft C++ Build Tools (Windows only)</summary>

Use the instructions [here](https://visualstudio.microsoft.com/visual-cpp-build-tools/) to install or update Microsoft C++ Build Tools.

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

## Prepare the Virtual Environment

Create the environment using a configuration file from the OpenBB Terminal repository.

Copy and paste these commands into the terminal/command prompt:

```shell
conda env create -n obb --file https://raw.githubusercontent.com/OpenBB-finance/OpenBBTerminal/main/build/conda/conda-3-9-env.yaml
```

:::note
Additional `YAML` files provide support for Python versions 3.8 and 3.10.  Substitute the `9`, in the command above, with the desired version.
:::

Agree to the prompts if there are any.

After the obb environment is created, activate it by entering:

```shell
conda activate obb
```

## Install the OpenBB Terminal and SDK

Make sure to have completed all previous steps. If followed, there will be a virtual environment, named `obb`, and this environment is activated.

Install the main package of Openbb SDK with `pip`, a package manager.

```shell
pip install openbb --no-cache-dir
```

This method provides access to the data aggregation and charting functions of the OpenBB SDK. It does not provide access to the advanced features that are provided by the Portfolio Optimization and Machine Learning toolkits.

The toolkits can be installed individually with:

```shell
pip install "openbb[optimization]" --no-cache-dir
```

and

```shell
pip install "openbb[forecast]" --no-cache-dir
```

Install all available toolkits at once with:

```shell
pip install "openbb[all]" --no-cache-dir
```

:::info
`pip install openbb[all]` is not yet compatible with environments such as Google Colab and Kaggle as they come with preinstalled packages that can conflict with the ones used in the OpenBBTerminal and SDK.  It may be possible to install without the extra toolkits, but we currently do not officially support this type of installation.  We are working on a solution to this problem and will update this section once it is resolved.
:::

## Verify Installation

Once this installation process is completed, the terminal is launched by running:

```shell
openbb
```

To confirm the installation of the SDK, open the Python interpreter with a `python` command, then run the following:

```python
from openbb_terminal.sdk import openbb
openbb.__version__
```

You should see the version number displayed, for example:

```console
'3.0.1'
```

That's it!

**NOTE:** When the OpenBB Terminal is opened next, the Python environment will need to be activated again. When using a code editor, make sure that the correct environment is selected. This should be easy to figure out if there is an error stating that there are missing packages. To launch the OpenBB Terminal application in a new terminal window, first navigate into the folder where the source code was cloned, and then use the following two commands:

```shell
conda activate obb
openbb
```

## Updating the OpenBB SDK Version

Upgrade the OpenBB SDK to the latest version via `pypi`. When using the terminal or SDK without toolkits, first activate  environment by running:

```shell
conda activate obb
```

and then update the package by running:

```shell
pip install -U openbb --no-cache-dir
```

When using an installation with toolkits, with the virtual environment activated, enter:

```shell
pip install -U "openbb[all]" --no-cache-dir
```

## Nightly Builds

OpenBB SDK is updated daily with new features and bug fixes, but some features being worked on may be unstable. To use the same SDK version as the development team, install the nightly build with:

```shell
conda activate obb
pip install -U openbb-nightly --no-cache-dir
```

:::info
If issues are encountered with the installation, please try installing OpenBB Terminal and SDK from source [(link)](/terminal/installation/source), or reach out to our [Discord](https://discord.gg/Up2QGbMKHY) community for help.
:::
