---
title: Launching
sidebar_position: 2
description: Help and troubleshooting when experiencing errors when launching the OpenBB Termainl.
keywords:
  [
    installation,
    installer,
    install,
    guide,
    mac,
    windows,
    linux,
    python,
    github,
    macos,
    how to,
    explanation,
    openbb terminal,
    ssl,
    certificate,
    launch,
    invalid cpu,
    fail to launch,
    fontconfig,
    linux,
    ubuntu
  ]
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Launching - Terminal | OpenBB Docs" />

<details><summary>Mac: Invalid CPU Type - Terminal fails to launch.</summary>

This error is usually the result of a Mac M1/M2 machine which does not have Rosetta installed. Install from the system Terminal command line:

```console
softwareupdate --install-rosetta
```

</details>

<details><summary>Incompatible library version: libtiff.6.dylib requires version 10.0.0 or later, but liblzma.5.dylib provides version 8.0.0</summary>

This issue can be resolved by following the steps below.

- Show hidden files
  - Command + Shift + . (period)
- Then go to Applications folder > OpenBB Terminal > .OpenBB
  - Find the file "liblzma.5.dylib" and remove it.
- Relaunch the terminal.

</details>

<details><summary>Terminal app does not launch: Failed to execute script 'terminal' due to unhandled exception!</summary>

When an installer-packaged version of the OpenBB Terminal fails to launch, because of this message, the machine may have an obsolete CPU-type or operating system. Please try installing via the source code, and if problems persist, reach out to us on [Discord](https://discord.gg/xPHTuHCmuV) or fill out a support request form on our [website](https://openbb.co/support).

</details>

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

<details><summary>Fontconfig warning: ignoring UTF-8: not a valid region tag</summary>

In the OS default terminal shell profile, check for a variable similar to, “set locale environment variables at startup”, then also, set text encoding to UTF-8.

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

<details><summary> Linux Ubuntu installation was successful but now hangs on launch.</summary>

Check that VcXsvr - or an equivalent X-host - is running and configured prior to launch.

</details>
