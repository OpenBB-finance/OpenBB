---
title: Import Errors
sidebar_position: 2
description: This page provides solutions for common import errors when installing
  the OpenBB SDK, including guidance on managing virtual environments, handling ModuleNotFoundError,
  dealing with SSL certificate authorization, and configuring proxy connections.
keywords:
- Import Errors
- SciPy
- ModuleNotFoundError
- virtual environment
- poetry install
- conda activate
- Jupyter
- GitHub
- SSL certificates
- firewall
- pip-system-certs
- proxy connection
- .env file
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Import Errors - Faqs | OpenBB SDK Docs" />

When packages not included in the OpenBB installation are installed to the same environment as the SDK, it is possible that an incompatible build of a specific library (like SciPy) has overwritten the existing and creating a conflict. In this event, try creating a new environment containing only the OpenBB dependencies.

<details><summary>ModuleNotFoundError: No module named '______'</summary>

Before troubleshooting please verify that the recommended installation instructions were followed. These errors often can occur when the virtual environment has not been activated, or the `poetry install` command was skipped. Activate the OpenBB virtual environment created during the installation process prior to launching or importing the SDK.

**Terminal**:

```console
conda activate obb
python terminal.py
```

**SDK**:

```console
conda activate obb
ipython
from openbb_terminal.sdk import openbb
```

**Jupyter**:

Check that the kernel selected for the session is the OpenBB virtual environment created during the installation process and then re-run the cell.

```console
from openbb_terminal.sdk import openbb
```

There is also a possibility that a new dependency has been added to the code and it has not yet been installed in the environment. This may happen after updating the code from GitHub, but before running the `poetry install` install command.

```console
poetry install -E all
```

</details>

<details><summary>SSL certificates fail to authorize</summary>

```console
SSL: CERTIFICATE_VERIFY_FAILED
```

An error message, similar to above, is usually encountered while attempting to use the OpenBB Platform from behind a firewall.  A workplace environment is typically the most common occurrence.  Try connecting to the internet directly through a home network to test the connection. If using a work computer and/or network,  we recommend speaking with the company's IT department prior to installing or running any software.

A potential solution is to try:

```console
pip install pip-system-certs
```

</details>

<details><summary>Cannot connect due to proxy connection.</summary>

Find the `.env` file (located at the root of the user account folder: (`~/.openbb_terminal/.env`), and add a line at the bottom of the file with:

```console
HTTP_PROXY="<ADDRESS>" or HTTPS_PROXY="<ADDRESS>”
```

</details>
