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
- CLI
- installation
- pip
- pypi

---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Installation | OpenBB CLI Docs" />

The OpenBB CLI is a wrapper around the OpenBB Platform, its requirements are the same and its components rely on your specific configuration of installed components. Please refer to the [OpenBB Platform install documentation](/platform/installation) for more information.

### PyPI

Within your existing OpenBB environment, install `openbb-cli` with:

```console
pip install openbb-cli
```

:::info
If you do not already have the OpenBB Platform packages installed, this will install the Core packages
:::

The installation script adds `openbb` to the PATH within your Python environment. The application can be launched from any path, as long as the environment is active.

```console
openbb

Welcome to OpenBB Platform CLI v1.0.0
```
