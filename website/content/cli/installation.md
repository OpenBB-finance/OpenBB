---
title: Installation
sidebar_position: 1
description: This page presents the general system requirements, supported environments,
  installation procedures, and setup for running the OpenBB Platform. It discusses
  the prerequisites including Python version, operating system requirements, Docker
  usage, and the process of building the platform from source.
keywords:
- OpenBB Platform
- Python
- System requirements
- Supported environments
- Installation
- Docker
- Python virtual environment
- Installation from source
- Windows 10
- Mac OS Big Sur
- Linux
- Package installation
- VS Code
- PyCharm
- Jupyter
- GitHub
- Conda
- venv
- API
- Repository
- pip
- Poetry
- Toml
- PyPI
- Node.js
- npm
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Installation | OpenBB Platform Docs" />

## General Requirements and Environments

Since the OpenBB Platform CLI is a wrapper around the OpenBB Platform, its requirements are the same. Please refer to the [OpenBB Platform install documentation](/platform/installation) for more information.

## Installation

Before installation, update the package manager so that `pip` is current, then create the environment with the desired version of Python.

:::note
Installing packages directly to the system Python or `base` environment is not recommended.  Create a new environment first (can be any name, using openbb here for example).

```bash
conda create -n openbb-cli python=3.11
conda activate openbb-cli
```

:::

### PyPI

Install from PyPI with:

```console
pip install openbb-cli
```

This will install the core OpenBB Platform CLI, along with officially supported Platform's extensions and providers.

#### Extensions

To install all extensions and providers (both officially supported and community maintained ones):

```console
pip install openbb[all]
```

To install a single extension:

```console
pip install openbb[charting]
```

```console
pip install openbb[ta]
```

Or install a single provider:

```console
pip install openbb[yfinance]
```

### Source

To build the OpenBB Platform from the source code, first install `git`:

```console
pip install git
```

Next, clone the repository from GitHub:

```console
git clone git@github.com:OpenBB-finance/OpenBBTerminal.git
```

When it is done, checkout the branch where the code is living:

```console
git checkout develop
```

Then, `cd` into the directory:

```console
cd cli
```

Install required packages

```console
pip install poetry
```

Finally, run `poetry` to install all dependencies:

```console
poetry install
```

## Post-Installation

You're ready to launch the OpenBB Platform CLI. To do so, run the following command:

```console
openbb
```