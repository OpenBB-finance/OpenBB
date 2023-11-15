---
title: Manage Extensions
sidebar_position: 3
description: Learn about the OpenBB Platform, an open-source solution built by the
  community. Understand its use via Python interface and REST API, and acquaint yourself
  with how to build a custom extension or contribute directly to the platform
keywords:
- OpenBB Platform
- Open source
- Python interface
- REST API
- Data integration
- Data standardization
- OpenBB extensions
- openbb-core
- Python package
- High-Level Architecture
- Custom extension
- Contribution
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Manage Extensions - Contributor Guidelines - Contributing | OpenBB Platform Docs" />

To install an extension hosted on PyPI, use the `pip install <extension>` command.

To install an extension that is developed locally, ensure that it contains a `pyproject.toml` file and then use the `pip install <extension>` command.

> To install the extension in editable mode using pip, add the `-e` argument.

Alternatively, for local extensions, you can add this line in the `LOCAL_DEPS` variable in `dev_install.py` file:

```toml
# If this is a community dependency, add this under "Community dependencies",
# with additional argument optional = true
openbb-extension = { path = "<relative-path-to-the-extension>", develop = true }
```

Now you can use the `python dev_install.py [-e]` command to install the local extension.

## Add an extension as a dependency

To add the `openbb-qa` extension as a dependency, you'll need to add it to the `pyproject.toml` file:

```toml
[tool.poetry.dependencies]
openbb-qa = "^0.0.0a2"
```

Then you can follow the same process as above to install the extension.
