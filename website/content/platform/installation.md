---
title: Installation
sidebar_position: 1
description: The OpenBB Platform provides the core architecture and services to interact with data providers and extensions.
keywords: [installation, installer, install, guide, mac, windows, linux, python, github, macos, how to, explanation, openbb, sdk, api, pip, pypi,]
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Installation - Platform | OpenBB Docs" />

## Virtual Environment

The OpenBB Platform is installed within a Python virtual environment.  It is compatible with versions of Python between 3.8 and 3.11, inclusively.  Before installation, update the package manager so that `pip` is current, then create the environment with the desired version of Python and install the following packages:

:::note
Installing packages directly to the system Python or `base` environment is not recommended.  Create a new environment.
:::

```console
pip install poetry toml
```

## Source

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
git checkout feature/openbb-sdk-v4
```

Then, `cd` into the directory:

```console
cd openbb_platform
```

Finally, run the developer installation script:

```console
python dev_install.py
```

:::note
To install all extensions and providers, run: `python dev_install.py -e`
:::

With a fresh installation, or upon installing or uninstalling extensions, the Python interface needs to be built.  This is done automatically, but can be manually triggered if required.  Start a Python session and then `import openbb`:

```console
python

import openbb

exit()
```

To manually trigger the build:

```python
import openbb
openbb.build()
```

Restart the Python interpreter and then begin using the OpenBB Platform.

```python
from openbb import obb
```

Start the REST API with:

```console
uvicorn openbb_core.api.rest_api:app --host 0.0.0.0 --port 8000 --reload
```

