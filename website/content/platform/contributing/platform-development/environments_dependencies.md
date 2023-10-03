---
title: Setup your development environment
sidebar_position: 2
description: Learn how to setup your development environment for the OpenBB Platform.
keywords: [openbb platform, introduction, environment, setup, contributing, documentation]
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Environment Setup - Platform | OpenBB Docs" />

In order to contribute to the OpenBB Platform, you need to setup your environment to ensure a smooth development experience.

<details>
<summary>Need help setting up Miniconda or Git?</summary>

Sometimes, installing Miniconda or Git can be a bit tricky, so we've prepared a set of instructions to help you get started.

Please refer to [OpenBBTerminal docs](https://docs.openbb.co/terminal/installation/source) for more information.
</details>

1. Clone the repository:

    ```bash
    git clone git@github.com:OpenBB-finance/OpenBBTerminal.git
    ```

2. Create and activate a virtual environment:

    > Supported python versions: python = ">=3.8,<3.12"

    ```bash
    conda create -n "obb-dev" python=3.9.13
    conda activate obb-dev
    ```

3. Manage your environment with [Poetry](https://python-poetry.org/):

    ```bash
    pip install poetry
    ```

4. Install the packages using the `dev_install.py` script located in the `openbb_platform` folder:

    ```bash
    python dev_install.py
    ```

   > To install all the packages, including extras, use the `-e` argument with the above script.

5. Setup your API keys locally by adding them to the `~/.openbb_platform/user_settings.json` file. Populate this file with the following template and replace the values with your keys:

  ```json
  {
    "credentials": {
      "fmp_api_key": "REPLACE_ME",
      "polygon_api_key": "REPLACE_ME",
      "benzinga_api_key": "REPLACE_ME",
      "fred_api_key": "REPLACE_ME"
    }
  }
  ```

  > You can also setup and use your keys from the OpenBB Hub and the Python interface at runtime. Follow the steps in [API Keys](./README.md#api-keys) section to know more about it.
