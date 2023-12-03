---
title: OpenBB Platform Extensions
sidebar_position: 1
description: This page describes the types of extensions available for the OpenBB Platform.
keywords:
- OpenBB Platform
- Python client
- Fast API
- getting started
- extensions
- data providers
- data extensions
- function extensions
- endpoints
- community
- technical analysis
- quantitative analysis
- charting libraries
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Overview - Extensions | OpenBB Platform Docs" />

When the core OpenBB Platform package is installed, familiar components might be missing. This is to keep the core components as light as possible. The extension framework allows individual pieces to be installed and removed seamlessly within the environment, using only the desired data and toolkit extensions.

There are two primary types of extensions for the OpenBB Platform:

- [Data](/platform/extensions/data_extensions)
- [Toolkits](/platform/extensions/toolkit_extensions)

The OpenBB Core installation does not include any toolkit extensions. Install the OpenBB Platform with all data and toolkit extensions from PyPI with:

```python
pip install openbb[all]
```

When installing from source, navigate into the `openbb_platform` folder from the root of the project and enter:

```console
python dev_install.py -e
```

This installs all extensions in editable mode, and the Python interface is compiled in, `/openbb_platform/openbb/package`, instead of the environment's `site-packages` folder. The tables in the next pages lists extensions as either, Core or Community. The Core extensions are installed by default.
