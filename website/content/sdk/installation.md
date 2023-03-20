---
title: Installation
sidebar_position: 1
description: The OpenBB SDK provides programmatic access to all Terminal functions. This layer of code allows users to build their own tools and applications on top of the existing architecture. Follow these steps to install on a local machine.
keywords: [installation, installer, install, guide, mac, windows, linux, python, github, macos, how to, explanation, openbb, sdk, api, pip, pypi,]
---
The OpenBB SDK provides programmatic access to all Terminal functions and much more. This layer of code allows users to build their own tools and applications on top of the existing architecture. Follow these steps to install on a local machine.

:::note
If the OpenBB Terminal has already been installed from source code, no additional installation steps are required. **You already have the SDK installed.**
:::

## Minimal Installation

For users who have basic developer tools installed and are using Python through a virtual environment, we recommend the following minimal installation method:

```shell
pip install openbb
```

This method provides access to the data aggregation and charting functions of the OpenBB SDK. It does not provide access to the advanced features that are provided by the Portfolio Optimization and Machine Learning toolkits.

If need to use the SDK with the Machine Learning and Portfolio Optimization toolkits we recommend following the [Full Installation instructions](#full-installation).

## Full Installation

To access the full functionality of the SDK with all the default toolkits, we recommend installing the SDK from source code [(link)](/terminal/installation/source). This will enable you to use the SDK with all the toolkits and contribute to the OpenBB project.

However, if you already have [the requirements listed at the beginning of the source code installation instructions](/terminal/installation/source) installed on your system, you can alternatively install the SDK toolkits from PyPI.

Install both ML and Portfolio Optimization toolkits with:

```shell
pip install openbb[all]
```

Install the ML and Portfolio Optimization toolkits individually with:

```shell
pip install openbb[optimization]
```

and

```shell
pip install openbb[forecast]
```

## Verify Installation

Confirm the installation by opening the python interpreter with a `python` command and running the following:

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

When using a full installation, with the `obb` Python environment active, enter:

```shell
pip install -U openbb[all]
```
