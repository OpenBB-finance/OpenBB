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
If the OpenBB Platform is not already installed, the `openbb-cli` package  will install the default components.
:::

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

Next, navigate into the folder: `~/OpenBBTerminal/cli`

:::tip
The Python environment should have `toml` and `poetry` installed.

```bash
pip install toml poetry
```
:::

Finally, enter:

```console
poetry install
```

Alternatively, install locally with `pip`:

```bash
pip install -e .
```

## Installing New Modules

New extensions, or removals, are automatically added (removed) to the CLI on the next launch.
