---
title: Installation
sidebar_position: 2
description: This page provides installation instructions for the OpenBB Platform CLI.
keywords:
- OpenBB Platform
- Python
- CLI
- installation
- pip
- pypi

---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Installation | OpenBB Platform CLI Docs" />

## Pre-Requisites

The OpenBB Platform CLI is a wrapper around the [Platform](/platform), and should be installed along side an existing OpenBB installation.

- A Python virtual environment with a version between 3.9 and 3.11, inclusive, is required.

Please refer to the [OpenBB Platform install documentation](/platform/installation) for instructions and more information.

:::info
If the OpenBB Platform is not already installed, the `openbb-cli` package  will install all available components.
:::

### Windows

The machine may need to have an installation of Visual C++ Build Tools available. Download the elements highlighted in the images below.

<details>
<summary mdxType="summary">"Microsoft Visual C++ 14.0 or greater is required"</summary>

Download and install [C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/), restart the machine, then continue.

![image](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/ceb57be0-6dae-42f2-aca6-bf62ce7d6135)

![image](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/f8aef8fc-a080-4164-bd36-460714ec44f3)

</details>

### Linux Requirements

Linux users will need to take additional steps prior to installation.

#### Rust

Rust and Cargo must be installed, system-level, and in the PATH. Follow the instructions on-screen to install and add to PATH in the shell profile.

```bash
curl --proto '=https' --tlsv1.3 https://sh.rustup.rs -sSf | sh
```

#### Webkit

Next, install webkit.

- Debian-based / Ubuntu / Mint: `sudo apt install libwebkit2gtk-4.0-dev`

- Arch Linux / Manjaro: `sudo pacman -S webkit2gtk`

- Fedora: `sudo dnf install gtk3-devel webkit2gtk3-devel`


## PyPI

Within your existing OpenBB environment, install `openbb-cli` with:

```console
pip install openbb-cli
```

The installation script adds `openbb` to the PATH within your Python environment. The application can be launched from any path, as long as the environment is active.

```console
openbb

Welcome to OpenBB Platform CLI v1.0.0
```

## Source

Follow the instructions [here](/platform/installation#source) to clone the GitHub repo and install the OpenBB Platform from the source code.

Next, navigate into the folder: `~/OpenBBTerminal/openbb_platform`

:::tip
The Python environment should have `poetry` installed.

```bash
pip install poetry
```
:::

Finally, enter:

```console
python dev_install.py -e --cli
```

## Installing New Modules

New extensions, or removals, are automatically added (removed) to the CLI on the next launch.
