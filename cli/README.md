# OpenBB Platform CLI

[![Downloads](https://static.pepy.tech/badge/openbb)](https://pepy.tech/project/openbb)
[![LatestRelease](https://badge.fury.io/py/openbb.svg)](https://github.com/OpenBB-finance/OpenBB)

| OpenBB is committed to build the future of investment research by focusing on an open source infrastructure accessible to everyone, everywhere. |
| :---------------------------------------------------------------------------------------------------------------------------------------------: |
|              ![OpenBBLogo](https://user-images.githubusercontent.com/25267873/218899768-1f0964b8-326c-4f35-af6f-ea0946ac970b.png)               |
|                                                 Check our website at [openbb.co](www.openbb.co)                                                 |

## Overview

The OpenBB Platform CLI is a command line interface that wraps [OpenBB Platform](https://docs.openbb.co/platform).

It offers a convenient way to interact with the OpenBB Platform and its extensions, as well as automated data collection via OpenBB Routine Scripts.

Find the most complete documentation, examples, and usage guides for the OpenBB Platform CLI [here](https://docs.openbb.co/cli).

## Installation

The command below provides access to all the available OpenBB extensions behind the OpenBB Platform, find the complete list [here](https://my.openbb.co/app/platform/extensions).

```bash
pip install openbb-cli
```

> Note: Find the most complete installation hints and tips [here](https://docs.openbb.co/cli/installation).

After the installation is complete, you can deploy the OpenBB Platform CLI by running the following command:

```bash
openbb
```

Which should result in the following output:

![image](https://github.com/OpenBB-finance/OpenBB/assets/48914296/f606bb6e-fa00-4fc8-bad2-8269bb4fc38e)

## API keys

To fully leverage the OpenBB Platform you need to get some API keys to connect with data providers. Here are the 3 options on where to set them:

1. OpenBB Hub
2. Local file

### 1. OpenBB Hub

Set your keys at [OpenBB Hub](https://my.openbb.co/app/platform/credentials) and get your personal access token from <https://my.openbb.co/app/platform/pat> to connect with your account.

> Once you log in, on the Platform CLI (through the `/account` menu, all your credentials will be in sync with the OpenBB Hub.)

### 2. Local file

You can specify the keys directly in the `~/.openbb_platform/user_settings.json` file.

Populate this file with the following template and replace the values with your keys:

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
