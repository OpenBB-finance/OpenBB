# OpenBB Platform

[Read the documentation](https://docs.openbb.co/platform)

## Overview

The OpenBB Platform is created and maintained by the OpenBB team together with the contributions from hundreds of community members.

It provides a convenient way to access raw financial data from multiple data providers. The package comes with a ready to use REST API - this allows developers from any language to easily create applications on top of OpenBB Platform.

## Installation

Installation instructions, documentation and usage examples are located [here](https://docs.openbb.co/platform#what-is-the-openbb-platform)

```console
pip install openbb
```

Or install with all data provider and toolkit extensions:

```console
pip install "openbb[all]"
```

## Install for development

To develop the OpenBB Platform you need to have the following:

- Git
- Python 3.8 or higher
- Virtual Environment with `poetry` and `toml` packages installed
  - To install these packages activate your virtual environment and run `pip install poetry toml`

How to install the platform in editable mode?

  1. Activate your virtual environment
  1. Navigate into the `openbb_platform` folder
  1. Run `python dev_install.py -e` to install the packages in editable mode
