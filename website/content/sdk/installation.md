---
title: Installation
sidebar_position: 1
description: The OpenBB SDK provides programmatic access to all Terminal functions. This layer of code allows users to build their own tools and applications on top of the existing architecture. Follow these steps to install on a local machine.
keywords: [installation, installer, install, guide, mac, windows, linux, python, github, macos, how to, explanation, openbb, sdk, api, pip, pypi,]
---
The OpenBB SDK provides programmatic access to all Terminal functions and much more. This layer of code allows users to build their own tools and applications on top of the existing architecture.

:::note
If the OpenBB Terminal has already been installed from source code, no additional installation steps are required. **You already have the SDK installed.**
Verify the installation by following [these steps](#verify-installation).
:::

## Requirements

The OpenBB SDK is designed to be used in a virtual environment. __You should not try installing the SDK into your system python or your base conda enviromnent__. If you are not sure what this means, please follow the instructions to install OpenBB Terminal from source [(link)](/terminal/installation/source).

OpenBB SDK is available on [PyPI](https://pypi.org/project/openbb/). To install the SDK from PYPI you will need to meet the following requirements:

- Use Python 3.8, 3.9, or 3.10
- Use Python from a virtual environment
- Have a C compiler installed (e.g. `gcc`, `clang`, etc.). These usually come with the operating system.
- Have `cmake` installed on your machine. This is usually available through your package manager (e.g. `apt`, `brew`, `yum`, etc.).

:::info
If you encounter any issues with the installation, please try following the instructions to install OpenBB Terminal from source [(link)](/terminal/installation/source).
:::

## Minimal Installation

To install from PyPI, activate your virtual environment and enter:

```shell
pip install openbb
```

This method provides access to the data aggregation and charting functions of the OpenBB SDK. It does not provide access to the advanced features that are provided by the Portfolio Optimization and Machine Learning toolkits.

The toolkits can be installed individually with:

```shell
pip install openbb[optimization]
```

and

```shell
pip install openbb[forecast]
```

Install all available toolkits at once with:

```shell
pip install openbb[all]
```

:::info
If you encounter any issues with the installation, please try following the instructions to install OpenBB Terminal from source [(link)](/terminal/installation/source).
:::

## Verify Installation

To confirm the installation, activate your virtual environment and open the Python interpreter with a python command, then run the following:

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

When using an installation with toolkits, with your virtual environment activated, enter:

```shell
pip install -U openbb[all]
```

## Nightly Builds

OpenBB SDK is updated daily with new features and bug fixes, but some features being worked on may be unstable. To use the same SDK version as the development team, install the nightly build with:

```shell
pip install -U openbb-nightly
```
